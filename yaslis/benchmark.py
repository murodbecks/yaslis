import time
import tracemalloc
import random
import json
import statistics
from tqdm import tqdm
from pathlib import Path
from typing import Dict, List, Tuple, Callable
from yaslis.library import Library
from yaslis.utils import check_type, get_processor_name

CPU_NAME = get_processor_name()

class BenchmarkResults:
    """Container for benchmark results"""
    
    def __init__(self, dataset_size: int, method_name: str):
        self.dataset_size = dataset_size
        self.method_name = method_name
        self.times = []
        self.memory_usage = []
        self.success_rate = 0.0
    
    def add_measurement(self, time_taken: float, memory_used: int, success: bool):
        self.times.append(time_taken)
        self.memory_usage.append(memory_used)
    
    def get_stats(self) -> Dict:
        return {
            'dataset_size': self.dataset_size,
            'method_name': self.method_name,
            'avg_time_ms': statistics.mean(self.times) * 1000,
            'std_time_ms': statistics.stdev(self.times) * 1000 if len(self.times) > 1 else 0,
            'avg_memory_kb': statistics.mean(self.memory_usage) / 1024,
            'std_memory_kb': statistics.stdev(self.memory_usage) / 1024 if len(self.memory_usage) > 1 else 0,
            'success_rate': self.success_rate,
            'num_experiments': len(self.times)
        }

class LibraryBenchmark:
    """Benchmark different search and recommendation methods"""
    
    def __init__(self, library: Library, output_dir: str = "benchmarks"):
        check_type(library, Library, "library")
        check_type(output_dir, str, "output_dir")
        
        self.library = library
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Available methods to benchmark
        self.search_methods = {
            'basic_search': self._benchmark_basic_search,
            'improved_search': self._benchmark_improved_search
        }
        
        self.recommendation_methods = {
            'basic_recommendation': self._benchmark_basic_recommendation,
            'improved_recommendation': self._benchmark_improved_recommendation
        }
    
    def generate_test_sizes(self, max_size: int, num_levels: int = 6) -> List[int]:
        """Generate exponentially spaced test sizes"""
        if max_size <= 0:
            return [len(self.library.get_books())]
        
        # Generate sizes: max_size / (2^(n-1)) for n from num_levels to 1
        sizes = []
        for i in range(num_levels, 0, -1):
            size = max_size // (2 ** (i-1))
            if size > 0:
                sizes.append(size)
        
        # Ensure we don't exceed available books
        available_books = len(self.library.get_books())
        return [min(size, available_books) for size in sizes if size <= available_books]
    
    def _create_test_library_book_first(self, size: int) -> Library:
        """Fallback method: original book-first approach"""
        all_books = self.library.get_books()

        test_library = Library()
        sampled_books = random.sample(all_books, size)
        
        for book in sampled_books:
            test_library.add_book(
                book.get_id(),
                book.get_title(),
                book.get_author(),
                book.get_genre(),
                book.get_published_year(),
                book.get_rating()
            )
        
        return test_library

    def create_test_library(self, size: int) -> Library:
        """Create library by strategically sampling users and their books"""
        all_books = self.library.get_books()
        all_users = self.library.get_users()

        if size >= len(all_books):
            return self.library
    
        test_library = Library()
        selected_book_titles = []
        
        random.shuffle(all_users)
        for user in all_users:
            user_books = user.get_all_books()
            if len(selected_book_titles) + len(user_books) > size:
                break
                
            for book in user_books:
                if book.get_title() not in selected_book_titles:
                    selected_book_titles.append(book.get_title())
                    test_library.add_book(
                        book.get_id(),
                        book.get_title(),
                        book.get_author(),
                        book.get_genre(),
                        book.get_published_year(),
                        book.get_rating()
                    )
            
            test_library.add_user(
                user.get_id(),
                user.get_name(),
                user.get_borrowed_books(),
                user.get_history()
                )
        
        # If we still need more books, add random ones
        if len(selected_book_titles) < size:
            remaining_books = [book for book in all_books if book.get_title() not in selected_book_titles]
            additional_needed = size - len(selected_book_titles)
            additional_books = random.sample(remaining_books, min(additional_needed, len(remaining_books)))
            
            for book in additional_books:
                test_library.add_book(
                    book.get_id(),
                    book.get_title(),
                    book.get_author(),
                    book.get_genre(),
                    book.get_published_year(),
                    book.get_rating()
                )
        
        return test_library
    
    def create_eval_set(self, test_library: Library, num_experiments: int = 100) -> List[str]:
        """Create evaluation set of book titles to search for"""
        available_titles = test_library.get_book_titles()
        if not available_titles:
            return []
        
        # Sample titles (with replacement if needed)
        eval_size = min(num_experiments, len(available_titles))
        return random.choices(available_titles, k=eval_size)
    
    def _measure_method(self, method: Callable, *args) -> Tuple[float, int, bool]:
        """Measure time and memory usage of a method call"""
        # Start memory tracking
        tracemalloc.start()
        
        # Measure time
        start_time = time.perf_counter()
        try:
            result = method(*args)
            success = result is not None and (
                isinstance(result, list) or 
                hasattr(result, 'get_title')
            )
        except Exception:
            result = None
            success = False
        end_time = time.perf_counter()
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        time_taken = end_time - start_time
        return time_taken, peak, success
    
    def _benchmark_basic_search(self, test_library: Library, query: str) -> Tuple[float, int, bool]:
        """Benchmark basic search method"""
        return self._measure_method(test_library.search_book, query)
    
    def _benchmark_improved_search(self, test_library: Library, query: str) -> Tuple[float, int, bool]:
        """Benchmark improved search method"""
        return self._measure_method(test_library.search_book_improved, query)
    
    def _benchmark_basic_recommendation(self, test_library: Library, num_recs: int = 10) -> Tuple[float, int, bool]:
        """Benchmark basic recommendation method"""
        return self._measure_method(test_library.recommend_books, num_recs)
    
    def _benchmark_improved_recommendation(self, test_library: Library, num_recs: int = 10) -> Tuple[float, int, bool]:
        """Benchmark improved recommendation method"""
        available_users = test_library.get_users()

        if not available_users:
            print("No users with history found, falling back to basic recommendation")
            return self._measure_method(test_library.recommend_books, num_recs)
        
        random_user = random.choice(available_users)
        
        return self._measure_method(test_library.recommend_books_improved, random_user, num_recs)
    
    def benchmark_search_methods(self, test_sizes: List[int], num_experiments: int = 100) -> Dict[str, List[BenchmarkResults]]:
        """Benchmark all search methods across different dataset sizes"""
        results = {method_name: [] for method_name in self.search_methods.keys()}
        
        for size in tqdm(test_sizes, desc="Benchmarking search methods"):
            test_library = self.create_test_library(size)
            eval_set = self.create_eval_set(test_library, num_experiments)
            
            for method_name, benchmark_func in self.search_methods.items():
                benchmark_result = BenchmarkResults(size, method_name)
                successful_searches = 0
                
                for query in eval_set:
                    time_taken, memory_used, success = benchmark_func(test_library, query)
                    benchmark_result.add_measurement(time_taken, memory_used, success)
                    if success:
                        successful_searches += 1
                
                benchmark_result.success_rate = successful_searches / len(eval_set) if eval_set else 0
                results[method_name].append(benchmark_result)
                        
        return results
    
    def benchmark_recommendation_methods(self, test_sizes: List[int], num_experiments: int = 50) -> Dict[str, List[BenchmarkResults]]:
        """Benchmark all recommendation methods across different dataset sizes"""
        results = {method_name: [] for method_name in self.recommendation_methods.keys()}
        
        for size in tqdm(test_sizes, desc="Benchmarking recommendation methods"):
            test_library = self.create_test_library(size)
            
            for method_name, benchmark_func in self.recommendation_methods.items():
                benchmark_result = BenchmarkResults(size, method_name)
                successful_recommendations = 0
                
                for _ in range(num_experiments):
                    time_taken, memory_used, success = benchmark_func(test_library, 10)
                    benchmark_result.add_measurement(time_taken, memory_used, success)
                    if success:
                        successful_recommendations += 1
                
                benchmark_result.success_rate = successful_recommendations / num_experiments
                results[method_name].append(benchmark_result)
        
        return results
    
    def run_full_benchmark(self, num_experiments: int = 100) -> Dict:
        """Run complete benchmark suite"""
        num_books = len(self.library.get_books())
        
        # Generate test sizes
        test_sizes = self.generate_test_sizes(num_books)
        
        # Run benchmarks
        search_results = self.benchmark_search_methods(test_sizes, num_experiments)
        recommendation_results = self.benchmark_recommendation_methods(test_sizes, num_experiments // 2)
        
        # Combine results
        all_results = {
            'metadata': {
                'total_books': num_books,
                'test_sizes': test_sizes,
                'processor': CPU_NAME,
                'num_experiments': num_experiments,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'search_results': search_results,
            'recommendation_results': recommendation_results
        }
        
        return all_results
    
    def save_results(self, results: Dict, filename: str = None) -> Path:
        """Save benchmark results to JSON file"""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            cpu_name = CPU_NAME.replace(" ", "_")
            filename = f"{cpu_name}_{timestamp}.json" if len(cpu_name) > 1 else f"results_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        # Convert BenchmarkResults to dictionaries
        serializable_results = {
            'metadata': results['metadata'],
            'search_results': {
                method: [result.get_stats() for result in result_list]
                for method, result_list in results['search_results'].items()
            },
            'recommendation_results': {
                method: [result.get_stats() for result in result_list]
                for method, result_list in results['recommendation_results'].items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        return output_path
    
    def print_summary(self, results: Dict):
        """Print a summary of benchmark results"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        metadata = results['metadata']
        print(f"Total books available: {metadata['total_books']}")
        print(f"Test sizes: {metadata['test_sizes']}")
        print(f"Testing machine: {metadata['processor']}")
        print(f"Experiments per size: {metadata['num_experiments']}")
        print(f"Timestamp: {metadata['timestamp']}")
        
        # Search methods summary
        print("\nSEARCH METHODS:")
        print("-" * 40)
        for method_name, result_list in results['search_results'].items():
            print(f"\n{method_name.upper()}:")
            for result in result_list:
                stats = result.get_stats()
                print(f"  Size {stats['dataset_size']:>6}: "
                      f"{stats['avg_time_ms']:>8.3f}ms ± {stats['std_time_ms']:>6.3f}ms | "
                      f"{stats['avg_memory_kb']:>8.1f}KB | "
                      f"Success: {stats['success_rate']*100:>5.1f}%")
        
        # Recommendation methods summary
        print("\nRECOMMENDATION METHODS:")
        print("-" * 40)
        for method_name, result_list in results['recommendation_results'].items():
            print(f"\n{method_name.upper()}:")
            for result in result_list:
                stats = result.get_stats()
                print(f"  Size {stats['dataset_size']:>6}: "
                      f"{stats['avg_time_ms']:>8.3f}ms ± {stats['std_time_ms']:>6.3f}ms | "
                      f"{stats['avg_memory_kb']:>8.1f}KB | "
                      f"Success: {stats['success_rate']*100:>5.1f}%")

# Usage example
if __name__ == "__main__":
    # Load library
    library = Library('configs/sample_books.jsonl', 'configs/sample_users.jsonl')
    
    # Create benchmark
    benchmark = LibraryBenchmark(library)
    
    # Run benchmark (adjust max_size as needed)
    results = benchmark.run_full_benchmark(num_experiments=100)
    
    # Save and display results
    benchmark.save_results(results)
    benchmark.print_summary(results)
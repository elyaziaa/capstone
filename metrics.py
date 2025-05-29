import psutil
import subprocess
import time
import threading
import os
import ast
import platform
import re

class CyclomaticComplexityCalculator:
    """Calculate cyclomatic complexity for multiple programming languages"""
    
    def __init__(self):
        self.complexity = 0
    
    def calculate_complexity(self, file_path, code_content):
        """Calculate cyclomatic complexity based on file extension"""
        ext = os.path.splitext(file_path.lower())[1]
        
        if ext == '.py':
            return self.analyze_python(code_content)
        elif ext in ['.java']:
            return self.analyze_java(code_content)
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            return self.analyze_javascript(code_content)
        elif ext in ['.c', '.cpp', '.cc', '.cxx', '.h', '.hpp']:
            return self.analyze_c_cpp(code_content)
        elif ext == '.go':
            return self.analyze_go(code_content)
        elif ext in ['.cs']:
            return self.analyze_csharp(code_content)
        elif ext in ['.php']:
            return self.analyze_php(code_content)
        elif ext in ['.rb']:
            return self.analyze_ruby(code_content)
        else:
            return self.analyze_generic(code_content)
    
    def analyze_python(self, code_content):
        """Analyze Python using AST"""
        try:
            tree = ast.parse(code_content)
            self.complexity = 1  # Base complexity
            self.visit_python_node(tree)
            return self.complexity
        except:
            return 0
    
    def visit_python_node(self, node):
        """Visit Python AST node"""
        if isinstance(node, ast.FunctionDef):
            self.complexity += 1
        elif isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            self.complexity += 1
        elif isinstance(node, (ast.ExceptHandler, ast.Try)):
            self.complexity += 1
        elif isinstance(node, ast.BoolOp):
            self.complexity += len(node.values) - 1
        elif isinstance(node, ast.IfExp):
            self.complexity += 1
        elif isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            for generator in node.generators:
                if generator.ifs:
                    self.complexity += len(generator.ifs)
        elif isinstance(node, ast.Lambda):
            self.complexity += 1
        
        for child in ast.iter_child_nodes(node):
            self.visit_python_node(child)
    
    def analyze_java(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'else if', 'while', 'for', 'switch', 'case', 'catch', 
            'throw', 'throws', '&&', '||', '?', 'do'
        ])
    
    def analyze_javascript(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'else if', 'while', 'for', 'switch', 'case', 'catch', 
            'throw', '&&', '||', '?', 'do', 'function', '=>'
        ])
    
    def analyze_c_cpp(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'else if', 'while', 'for', 'switch', 'case', 'catch', 
            'throw', '&&', '||', '?', 'do'
        ])
    
    def analyze_go(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'else if', 'while', 'for', 'switch', 'case', 'defer',
            '&&', '||', 'func', 'go', 'select'
        ])
    
    def analyze_csharp(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'else if', 'while', 'for', 'foreach', 'switch', 'case', 
            'catch', 'throw', '&&', '||', '?', 'do'
        ])
    
    def analyze_php(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'elseif', 'while', 'for', 'foreach', 'switch', 'case', 
            'catch', 'throw', '&&', '||', '?', 'do', 'function'
        ])
    
    def analyze_ruby(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'elsif', 'while', 'for', 'case', 'when', 'rescue', 
            'raise', '&&', '||', '?', 'def', 'unless', 'until'
        ])
    
    def analyze_generic(self, code_content):
        return self.count_complexity_keywords(code_content, [
            'if', 'else', 'while', 'for', 'switch', 'case', 'catch', 
            'throw', '&&', '||', '?', 'function', 'def'
        ])
    
    def count_complexity_keywords(self, code_content, keywords):
        """Count complexity-contributing keywords in code"""
        cleaned_code = self.remove_comments_and_strings(code_content)
        complexity = 1  # Base complexity
        
        for keyword in keywords:
            if keyword in ['&&', '||']:
                pattern = r'\&\&|\|\|'
            elif keyword == '?':
                pattern = r'\?'
            elif keyword == '=>':
                pattern = r'=>'
            else:
                pattern = r'\b' + re.escape(keyword) + r'\b'
            
            matches = re.findall(pattern, cleaned_code, re.IGNORECASE)
            complexity += len(matches)
        
        return max(complexity, 1)
    
    def remove_comments_and_strings(self, code_content):
        """Remove comments and string literals to avoid false keyword matches"""
        # Remove single-line comments
        code_content = re.sub(r'//.*$', '', code_content, flags=re.MULTILINE)
        code_content = re.sub(r'#.*$', '', code_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        code_content = re.sub(r'/\*.*?\*/', '', code_content, flags=re.DOTALL)
        
        # Remove string literals
        code_content = re.sub(r'"[^"]*"', '""', code_content)
        code_content = re.sub(r"'[^']*'", "''", code_content)
        code_content = re.sub(r'`[^`]*`', '``', code_content)
        
        return code_content

class UniversalEnergyMonitor:
    def __init__(self):
        self.samples = []
        self.monitoring = False
        
    def monitor_process(self, process):
        """Monitor process for energy calculation"""
        while self.monitoring and process.is_running():
            try:
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.samples.append({
                    'cpu_percent': cpu_percent,
                    'memory_mb': memory_mb
                })
                time.sleep(0.1)  # Sample every 100ms
            except psutil.NoSuchProcess:
                break
    
    def measure_program_silent(self, command, source_file=None):
        """Measure program silently - no output shown, only results"""
        # Start the program with suppressed output
        process = subprocess.Popen(
            command, 
            shell=True,
            stdout=subprocess.DEVNULL,  # Suppress stdout
            stderr=subprocess.DEVNULL,  # Suppress stderr
            stdin=subprocess.DEVNULL    # Suppress stdin prompts
        )
        ps_process = psutil.Process(process.pid)
        
        # Start monitoring
        self.monitoring = True
        self.samples = []
        monitor_thread = threading.Thread(target=self.monitor_process, args=(ps_process,))
        monitor_thread.start()
        
        # Measure execution time
        start_time = time.time()
        process.wait()
        execution_time = time.time() - start_time
        
        # Stop monitoring
        self.monitoring = False
        monitor_thread.join()
        
        # Calculate metrics
        energy_consumption = self.calculate_energy_consumption(execution_time)
        cyclomatic_complexity = self.calculate_cyclomatic_complexity(source_file)
        
        return {
            'energy_consumption_wh': energy_consumption,
            'execution_time_s': execution_time,
            'cyclomatic_complexity': cyclomatic_complexity
        }
    
    def calculate_energy_consumption(self, duration):
        """Calculate energy consumption in Wh"""
        if not self.samples:
            return 0.0
            
        avg_cpu = sum(s['cpu_percent'] for s in self.samples) / len(self.samples)
        avg_memory = sum(s['memory_mb'] for s in self.samples) / len(self.samples)
        
        # Energy estimation based on CPU and memory usage
        base_power = 5  # watts (system baseline)
        cpu_power = (avg_cpu / 100) * 30  # CPU power contribution
        memory_power = (avg_memory / 1000) * 2  # Memory power contribution
        
        total_power = base_power + cpu_power + memory_power
        energy_wh = (total_power * duration) / 3600  # Convert to Wh
        
        return round(energy_wh, 6)
    
    def calculate_cyclomatic_complexity(self, source_file):
        """Calculate cyclomatic complexity from source code"""
        if not source_file or not os.path.exists(source_file):
            return "N/A"
        
        try:
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()
            
            calculator = CyclomaticComplexityCalculator()
            complexity = calculator.calculate_complexity(source_file, code_content)
            return complexity
            
        except Exception as e:
            return f"Error: {str(e)}"

def list_files_in_directory():
    """List all files in the current directory"""
    files = []
    print("\n=== Files in current directory ===")
    for i, item in enumerate(os.listdir('.'), 1):
        if os.path.isfile(item):
            files.append(item)
            print(f"{i}. {item}")
    return files

def get_file_command(filename):
    """Determine the appropriate command to run a file"""
    if not os.path.exists(filename):
        return None
        
    name, ext = os.path.splitext(filename.lower())
    
    # Use python3 on macOS/Linux, python on Windows
    python_cmd = "python3" if platform.system() in ["Darwin", "Linux"] else "python"
    
    commands = {
        '.py': f'{python_cmd} "{filename}"',
        '.js': f'node "{filename}"',
        '.jsx': f'node "{filename}"',
        '.ts': f'npx ts-node "{filename}"',
        '.tsx': f'npx ts-node "{filename}"',
        '.java': f'javac "{filename}" && java "{name}"',
        '.jar': f'java -jar "{filename}"',
        '.c': f'gcc "{filename}" -o "{name}" && ./"{name}"',
        '.cpp': f'g++ "{filename}" -o "{name}" && ./"{name}"',
        '.cc': f'g++ "{filename}" -o "{name}" && ./"{name}"',
        '.cxx': f'g++ "{filename}" -o "{name}" && ./"{name}"',
        '.go': f'go run "{filename}"',
        '.rs': f'rustc "{filename}" && ./"{name}"',
        '.cs': f'dotnet run "{filename}"',
        '.php': f'php "{filename}"',
        '.rb': f'ruby "{filename}"',
        '.pl': f'perl "{filename}"',
        '.exe': f'"{filename}"',
        '.sh': f'bash "{filename}"',
        '.bat': f'"{filename}"'
    }
    
    # For executable files without extension
    if ext == '' and os.access(filename, os.X_OK):
        return f'"{filename}"'
    
    return commands.get(ext)

def print_results_simple(result, program_name):
    """Print only the 3 metrics - clean and simple"""
    complexity = result['cyclomatic_complexity']
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {program_name}")
    print(f"{'='*60}")
    print(f"Energy Consumption:     {result['energy_consumption_wh']:.6f} Wh")
    print(f"Execution Time:         {result['execution_time_s']:.3f} seconds")
    print(f"Cyclomatic Complexity:  {complexity}")
    print(f"{'='*60}")

def main():
    monitor = UniversalEnergyMonitor()
    
    while True:
        print("\n" + "="*50)
        print("PROGRAM ANALYZER")
        print("="*50)
        
        print("\nChoose an option:")
        print("1. Analyze file (silent execution)")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == '1':
            # List files and let user select
            files = list_files_in_directory()
            
            if not files:
                print("No files found in current directory!")
                continue
                
            while True:
                try:
                    selection = input(f"\nEnter file number (1-{len(files)}) or filename: ").strip()
                    
                    if selection.isdigit():
                        file_index = int(selection) - 1
                        if 0 <= file_index < len(files):
                            selected_file = files[file_index]
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(files)}")
                    else:
                        if selection in files:
                            selected_file = selection
                            break
                        else:
                            print(f"File '{selection}' not found in directory")
                except ValueError:
                    print("Please enter a valid number or filename")
            
            # Get command for the file
            command = get_file_command(selected_file)
            
            if command:
                print(f"\nAnalyzing {selected_file}... (running silently)")
                try:
                    result = monitor.measure_program_silent(command, selected_file)
                    print_results_simple(result, selected_file)
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Cannot determine how to run '{selected_file}'.")
        
        elif choice == '2':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
class CPUSimulator:
    def __init__(self):
        self.reset()

    def reset(self, optimization=False):
        # Hardware state
        self.registers = {f"R{i}": 0 for i in range(1, 9)} 
        self.memory = {} 
        
        # Multi-Level Cache System
        self.l1_cache = {}  # Fast, Size 2
        self.l2_cache = {}  # Slower, Size 4
        self.l1_size = 2
        self.l2_size = 4
        
        # Program state
        self.instructions = []
        self.labels = {} # Stores memory addresses for LOOPs
        self.pc = 0 
        
        # 5-Stage Pipeline
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}
        
        self.optimization_enabled = optimization
        self.stall_cycles = 0
        
        # Advanced Stats
        self.stats = {
            "cycles": 0, 
            "completed_instructions": 0, 
            "hazards": 0,
            "l1_hits": 0, 
            "l1_misses": 0, 
            "l2_hits": 0, 
            "l2_misses": 0
        }

    def load_program(self, instruction_list):
        """The Syntax Checking Compiler"""
        self.instructions = []
        self.labels = {}
        cleaned_lines = []
        
        # Pass 1: Find labels (e.g., "LOOP:")
        for line in instruction_list:
            line = line.strip()
            if not line: 
                continue
            if line.endswith(':'):
                self.labels[line[:-1]] = len(cleaned_lines)
            else:
                cleaned_lines.append(line)
                
        # Pass 2: Syntax Validation (Includes SET and DIV)
        valid_ops = ['LOAD', 'STORE', 'ADD', 'SUB', 'MUL', 'DIV', 'JUMP', 'BEQ', 'BNE', 'SET']
        for idx, line in enumerate(cleaned_lines):
            parts = line.replace(',', '').split()
            op = parts[0]
            
            if op not in valid_ops:
                return False, f"Line {idx+1}: Unknown instruction '{op}'."
                
            if op in ['ADD', 'SUB', 'MUL', 'DIV', 'LOAD', 'STORE', 'SET'] and not parts[1].startswith('R'):
                return False, f"Line {idx+1}: '{parts[1]}' is not a valid register."
                
            if op in ['JUMP', 'BEQ', 'BNE']:
                target = parts[-1]
                if target not in self.labels:
                    return False, f"Line {idx+1}: Target label '{target}' does not exist."
                    
        self.instructions = cleaned_lines
        self.pc = 0
        return True, "Program Compiled Successfully!"

    def update_lru(self, cache, address):
        """Moves accessed address to the 'most recently used' end of the dictionary"""
        if address in cache:
            val = cache.pop(address)
            cache[address] = val

    def access_memory(self, address, write_val=None):
        """L1 and L2 Cache Simulation"""
        # Write operation
        if write_val is not None:
            self.memory[address] = write_val
            if address in self.l1_cache: 
                self.update_lru(self.l1_cache, address)
                self.l1_cache[address] = write_val
            if address in self.l2_cache: 
                self.update_lru(self.l2_cache, address)
                self.l2_cache[address] = write_val
            return write_val

        # Read operation (Check L1)
        if address in self.l1_cache:
            self.stats["l1_hits"] += 1
            self.update_lru(self.l1_cache, address)
            return self.l1_cache[address]
        
        self.stats["l1_misses"] += 1

        # Check L2
        if address in self.l2_cache:
            self.stats["l2_hits"] += 1
            self.update_lru(self.l2_cache, address)
            val = self.l2_cache[address]
        else:
            self.stats["l2_misses"] += 1
            val = self.memory.get(address, 0)
            
            # Add to L2
            if len(self.l2_cache) >= self.l2_size: 
                del self.l2_cache[next(iter(self.l2_cache))]
            self.l2_cache[address] = val

        # Promote to L1
        if len(self.l1_cache) >= self.l1_size: 
            del self.l1_cache[next(iter(self.l1_cache))]
        self.l1_cache[address] = val
        
        return val

    def step(self):
        if self.stall_cycles > 0:
            self.stall_cycles -= 1
            self.stats["cycles"] += 1
            return

        self.stats["cycles"] += 1

        # 5. WRITEBACK (WB)
        wb_inst = self.pipeline["MEM"]
        self.pipeline["WB"] = wb_inst
        
        if wb_inst and "FLUSHED" not in wb_inst:
            self.stats["completed_instructions"] += 1
            parts = wb_inst.replace(',', '').split()
            op = parts[0]
            
            if op == "SET":
                self.registers[parts[1]] = int(parts[2])
                
            elif op == "LOAD":
                self.registers[parts[1]] = self.access_memory(int(parts[2]))
                
            elif op in ["ADD", "SUB", "MUL", "DIV"]:
                val1 = self.registers.get(parts[2], int(parts[2]) if parts[2].isdigit() else 0)
                val2 = self.registers.get(parts[3], int(parts[3]) if parts[3].isdigit() else 0) if len(parts) > 3 else 0
                
                if op == "ADD": 
                    self.registers[parts[1]] = val1 + val2
                elif op == "SUB": 
                    self.registers[parts[1]] = val1 - val2
                elif op == "MUL": 
                    self.registers[parts[1]] = val1 * val2
                elif op == "DIV": 
                    if val2 != 0:
                        self.registers[parts[1]] = val1 // val2 
                    else:
                        self.registers[parts[1]] = 0 

        # 4. MEMORY (MEM)
        mem_inst = self.pipeline["EX"]
        self.pipeline["MEM"] = mem_inst
        
        if mem_inst and "FLUSHED" not in mem_inst:
            parts = mem_inst.replace(',', '').split()
            if parts[0] == "STORE":
                self.access_memory(int(parts[2]), write_val=self.registers.get(parts[1], 0))

        # 3. EXECUTE (EX) & BRANCH RESOLUTION
        ex_inst = self.pipeline["ID"]
        self.pipeline["EX"] = ex_inst
        
        if ex_inst and "FLUSHED" not in ex_inst:
            parts = ex_inst.replace(',', '').split()
            branch_taken = False
            
            if parts[0] == "JUMP":
                branch_taken = True
                self.pc = self.labels[parts[1]]
                
            elif parts[0] in ["BEQ", "BNE"]:
                v1 = self.registers.get(parts[1], 0)
                v2 = self.registers.get(parts[2], int(parts[2]) if parts[2].isdigit() else 0)
                
                if (parts[0] == "BEQ" and v1 == v2) or (parts[0] == "BNE" and v1 != v2):
                    branch_taken = True
                    self.pc = self.labels[parts[3]]
            
            if branch_taken:
                self.pipeline["IF"] = "FLUSHED (Branch Penalty)"
                self.pipeline["ID"] = "FLUSHED (Branch Penalty)"
                self.stats["hazards"] += 1

        # 2. DECODE (ID)
        id_inst = self.pipeline["IF"]
        if "FLUSHED" not in str(id_inst):
            self.pipeline["ID"] = id_inst

        # 1. FETCH (IF)
        if self.pc < len(self.instructions) and self.pipeline["IF"] != "FLUSHED (Branch Penalty)":
            self.pipeline["IF"] = self.instructions[self.pc]
            self.pc += 1
        elif self.pipeline["IF"] == "FLUSHED (Branch Penalty)":
            self.pipeline["IF"] = None 
        else:
            self.pipeline["IF"] = None

    def get_stats(self): 
        return self.stats
        
    def get_pipeline_state(self): 
        return self.pipeline
        
    def get_registers(self): 
        return self.registers
        
    def get_caches(self): 
        return self.l1_cache, self.l2_cache
        
    def get_memory(self): 
        return self.memory
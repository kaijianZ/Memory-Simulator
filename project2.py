# Yanlin  Zhu        zhuy11
# Kaijian Zhong      zhongk

import sys
import copy


class Simulator(object):
    def __init__(self, size_d, arr_d):
        self.MEMORY_SIZE = 256
        self.memory = list('.' * self.MEMORY_SIZE)
        self.proc_size = size_d
        self.proc_arr = arr_d
        self.page_table = dict()

    def simulate(self):
        self.contiguous_loop('Next-Fit')
        print()
        self.contiguous_loop('First-Fit')
        print()
        self.contiguous_loop('Best-Fit')
        print()
        self.non_contiguous_loop()

    def contiguous_loop(self, add_type):
        print('time 0ms: Simulator started (Contiguous -- {})'.format(add_type))
        proc_arr_cp = copy.deepcopy(self.proc_arr)

        t = 0
        ext_t = 0
        last_pt = 0
        while len(proc_arr_cp):
            for i in sorted(proc_arr_cp.keys()):
                if sum(proc_arr_cp[i][0]) <= t:
                    print('time {}ms: Process {} removed:'.format(ext_t, i))
                    self.remove(i)
                    self.print_memory()
                    proc_arr_cp[i].pop(0)
                if not len(proc_arr_cp[i]):
                    proc_arr_cp.pop(i)
            for i in sorted(proc_arr_cp.keys()):
                if proc_arr_cp[i][0][0] == t:
                    print('time {}ms: Process {} arrived (requires {} frames'
                          ')'.format(ext_t, i, self.proc_size[i]))
                    if self.memory.count('.') < self.proc_size[i]:
                        print('time {}ms: Cannot place process {} -- skipped'
                              '!'.format(ext_t, i))
                        self.print_memory()
                        proc_arr_cp[i].pop(0)
                        if not len(proc_arr_cp[i]):
                            proc_arr_cp.pop(i)
                    elif add_type == 'First-Fit':
                        if not self.first_fit_add(list(i * self.proc_size[i])):
                            print('time {}ms: Cannot place process {} -- '
                                  'starting defragmentation'.format(ext_t,
                                                                    i))
                            time_used, last_pt, moved = self.defragmentation()
                            ext_t += time_used
                            print(
                                'time {}ms: Defragmentation complete (moved {}'
                                ' frames: {})'.format(ext_t, time_used,
                                                      ', '.join(moved)))
                            self.print_memory()
                            self.first_fit_add(list(i * self.proc_size[i]))
                        print('time {}ms: Placed process {}:'.format(ext_t, i))
                        self.print_memory()
                    elif add_type == 'Best-Fit':
                        if not self.best_fit_add(list(i * self.proc_size[i])):
                            print('time {}ms: Cannot place process {} -- '
                                  'starting defragmentation'.format(ext_t,
                                                                    i))
                            time_used, last_pt, moved = self.defragmentation()
                            ext_t += time_used
                            print(
                                'time {}ms: Defragmentation complete (moved {}'
                                ' frames: {})'.format(ext_t, time_used,
                                                      ', '.join(moved)))
                            self.print_memory()
                            self.best_fit_add(list(i * self.proc_size[i]))
                        print('time {}ms: Placed process {}:'.format(ext_t, i))
                        self.print_memory()
                    else:
                        last_pt = self.next_fit_add(
                            list(i * self.proc_size[i]), last_pt)
                        if not last_pt:
                            last_pt = self.next_fit_add(
                                list(i * self.proc_size[i]), 0)
                        if not last_pt:
                            print('time {}ms: Cannot place process {} -- '
                                  'starting defragmentation'.format(ext_t, i))
                            time_used, last_pt, moved = self.defragmentation()
                            ext_t += time_used
                            print(
                                'time {}ms: Defragmentation complete (moved {}'
                                ' frames: {})'.format(ext_t, time_used,
                                                      ', '.join(moved)))
                            self.print_memory()
                            last_pt = self.next_fit_add(
                                list(i * self.proc_size[i]), last_pt)
                        print('time {}ms: Placed process {}:'.format(ext_t, i))
                        self.print_memory()
            t += 1
            ext_t += 1
        print('time {}ms: Simulator ended'
              ' (Contiguous -- {})'.format(ext_t - 1, add_type))

    def print_memory(self):
        print('=' * 32)
        for i in range(8):
            print(''.join(self.memory[i * 32:(i + 1) * 32]))
        print('=' * 32)

    def next_fit_add(self, process, start):
        for i in range(start, len(self.memory) - len(process) + 1):
            if self.memory[i] != '.':
                continue
            if self.memory[i:i + len(process)] == list('.' * len(process)):
                self.memory[i:i + len(process)] = process
                return i + len(process)
        return False

    def first_fit_add(self, process):
        for i in range(len(self.memory) - len(process) + 1):
            if self.memory[i] != '.':
                continue
            if self.memory[i:i + len(process)] == list('.' * len(process)):
                self.memory[i:i + len(process)] = process
                return True
        return False

    def best_fit_add(self, process):
        i = 0
        partitions = (0, float('inf'))
        while i < len(self.memory):
            if self.memory[i] == '.':
                length = 1
                while i + length < len(
                        self.memory) and self.memory[i + length] == '.':
                    length += 1
                if partitions[1] > length >= len(process):
                    partitions = (i, length)
                i += length
            else:
                i += 1
        if partitions[1] != float('inf'):
            self.memory[partitions[0]:partitions[0] + len(process)] = process
            return True
        return False

    def remove(self, proc_id):
        self.memory = list(
            map(lambda x: '.' if x == proc_id else x, self.memory))

    def defragmentation(self):
        i = 0
        while i < self.MEMORY_SIZE and self.memory[i] != '.':
            i += 1
        while i < self.MEMORY_SIZE and self.memory[i] == '.':
            i += 1
        time_used = self.MEMORY_SIZE - i - self.memory[i:].count('.')
        moved_proc = ['.']
        for i in self.memory[i:]:
            if i not in moved_proc:
                moved_proc.append(i)
        moved_proc.remove('.')
        while '.' in self.memory:
            self.memory.remove('.')
        last_point = len(self.memory)
        self.memory[:] = self.memory + list(
            '.' * (self.MEMORY_SIZE - len(self.memory)))
        return time_used, last_point, moved_proc

    def print_page_table(self):
        print('PAGE TABLE [page,frame]:')
        for key in sorted(self.page_table.keys()):
            line = '{}:'.format(key)
            for i in range(1 + int(len(self.page_table[key]) / 10)):
                for item in self.page_table[key][10 * i:10 * i + 10]:
                    line += ' [{},{}]'.format(item[0], item[1])
                print(line.strip())
                line = ''

    def non_contiguous_add(self, process, t):
        if self.memory.count('.') < len(process):
            print('time {}ms: Cannot place process {} -- '
                  'skipped!'.format(t, process[0]))
            return False
        self.page_table[process[0]] = []
        p = 0
        for i in range(len(self.memory)):
            if self.memory[i] == '.':
                self.page_table[process[0]].append([p, i])
                self.memory[i] = process[0]
                p += 1
            if len(process) == p:
                print('time {}ms: Placed process {}:'.format(t, process[0]))
                return True

    def non_contiguous_loop(self):
        self.memory = list('.' * self.MEMORY_SIZE)
        runs = copy.deepcopy(self.proc_arr)
        running_p = dict()  # {proc_id: quit time}
        t = 0
        print('time {}ms: Simulator started (Non-contiguous)'.format(t))
        while len(running_p.keys()) + len(runs.keys()):
            removes = []
            for run_id in sorted(running_p.keys()):
                if running_p[run_id] == t:
                    print('time {}ms: Process {} removed:'.format(t, run_id))
                    self.remove(run_id)
                    self.page_table.pop(run_id)
                    self.print_memory()
                    self.print_page_table()
                    removes.append(run_id)
            for del_id in removes:
                running_p.pop(del_id, None)
            removes = []
            for pid in sorted(runs.keys()):
                if runs[pid][0][0] == t:
                    print('time {}ms: Process {} arrived (requires {'
                          '} frames)'.format(t, pid, self.proc_size[pid]))
                    proc = list(str(pid) * int(self.proc_size[pid]))
                    if self.non_contiguous_add(proc, t):
                        running_p[pid] = runs[pid][0][0] + runs[pid][0][1]
                    runs[pid].pop(0)
                    if len(runs[pid]) == 0:
                        removes.append(pid)
                    self.print_memory()
                    self.print_page_table()
            for del_id in removes:
                runs.pop(del_id, None)
            t += 1
        print('time {}ms: Simulator ended (Non-contiguous)'.format(t - 1))


if __name__ == "__main__":
    size_dict = dict()
    arr_dict = dict()

    processes = []
    if len(sys.argv) != 2:
        sys.stderr.write(
            'ERROR: Invalid arguments\nUSAGE: ./a.out'
            ' <input-file> <stats-output-file>')
        exit(1)
    file_name = sys.argv[1]
    with open(file_name, 'r') as f:
        text = f.read().split('\n')
    for i in text:
        i.strip()
        if len(i) and i[0] != '#':
            proc = i.split(' ')
            if len(proc) < 3:
                sys.stderr.write('ERROR: Invalid input file format')
                exit(1)
            size_dict[proc[0]] = int(proc[1])
            arr_dict[proc[0]] = []
            for arr_t in proc[2:]:
                arr_dict[proc[0]].append(list(map(int, arr_t.split('/'))))

    # construct a new simulator object
    Simulator = Simulator(size_dict, arr_dict)
    Simulator.simulate()

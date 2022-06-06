# rotors 1, 2, 3: from left to right, reflector is at left end

import itertools
from mimetypes import init


VERBOSE = False

def verbose(*params):
    if VERBOSE:
        print(*params)

alphabet = 'abcdefghijklmnopqrstuvwxyz'
dict26 = {x: i for i, x in enumerate(alphabet)}

class Enigma:
    def __init__(self, reflector: str, rotors: list, notches: list, ring_settings: list, init_settings: list = ['a', 'a', 'a'], plugboard = alphabet):
        self.ring_settings = ring_settings
        self.init_settings = init_settings

        self.rotor1_offset = dict26[ring_settings[0]]
        self.rotor1_forward = {i: (dict26[x] - i) for i, x in enumerate(rotors[0])}
        self.rotor1_init_pos = dict26[init_settings[0]]
        self.rotor1_pos = self.rotor1_init_pos
        self.rotor1_notch = dict26[notches[0]]
        self.rotor1_backward = {dict26[x]: (i - dict26[x]) for i, x in enumerate(rotors[0])}
        
        self.rotor2_offset = dict26[ring_settings[1]]
        self.rotor2_forward = {i: (dict26[x] - i) for i, x in enumerate(rotors[1])}
        self.rotor2_init_pos = dict26[init_settings[1]]
        self.rotor2_pos = self.rotor2_init_pos
        self.rotor2_notch = dict26[notches[1]]
        self.rotor2_backward = {dict26[x]: (i - dict26[x]) for i, x in enumerate(rotors[1])}

        self.rotor3_offset = dict26[ring_settings[2]]
        self.rotor3_forward = {i: (dict26[x] - i) for i, x in enumerate(rotors[2])}
        self.rotor3_init_pos = dict26[init_settings[2]]
        self.rotor3_pos = self.rotor3_init_pos
        self.rotor3_notch = dict26[notches[2]]
        self.rotor3_backward = {dict26[x]: (i - dict26[x]) for i, x in enumerate(rotors[2])}
        
        self.reflector = {i: (dict26[x] - i) for i, x in enumerate(reflector)}
        self.plugboard = {i: (dict26[x] - i) for i, x in enumerate(plugboard)}

        self.locked = False
        
    def reset(self):
        self.rotor1_pos = self.rotor1_init_pos
        self.rotor2_pos = self.rotor2_init_pos
        self.rotor3_pos = self.rotor3_init_pos
    

    def step(self, c):
        
        verbose('-----------------------------')
        verbose('keyboard input:', c)
        if not self.locked:
            self.step_for(1)
        verbose('rotors position:', alphabet[self.rotor1_pos] + alphabet[self.rotor2_pos] + alphabet[self.rotor3_pos])

        offset = dict26[c]
        offset = (offset + self.plugboard[offset]) % 26
        verbose('plugboard encryption:', alphabet[offset])
        offset = (offset + self.rotor3_forward[(offset - self.rotor3_offset + self.rotor3_pos) % 26]) % 26
        verbose('rotor3 encryption:', alphabet[offset])
        offset = (offset + self.rotor2_forward[(offset - self.rotor2_offset + self.rotor2_pos) % 26]) % 26
        verbose('rotor2 encryption:', alphabet[offset])
        offset = (offset + self.rotor1_forward[(offset - self.rotor1_offset + self.rotor1_pos) % 26]) % 26
        verbose('rotor1 encryption:', alphabet[offset])
        offset = (offset + self.reflector[offset]) % 26
        verbose('reflector encryption:', alphabet[offset])
        offset = (offset + self.rotor1_backward[(offset - self.rotor1_offset + self.rotor1_pos) % 26]) % 26
        verbose('rotor1 encryption:', alphabet[offset])
        offset = (offset + self.rotor2_backward[(offset - self.rotor2_offset + self.rotor2_pos) % 26]) % 26
        verbose('rotor2 encryption:', alphabet[offset])
        offset = (offset + self.rotor3_backward[(offset - self.rotor3_offset + self.rotor3_pos) % 26]) % 26
        verbose('rotor3 encryption:', alphabet[offset])
        offset = (offset + self.plugboard[offset]) % 26
        verbose('plugboard encryption:', alphabet[offset])

        return alphabet[offset]
    

    def step_for(self, number):
        for _ in range(number):
            if self.rotor2_pos == self.rotor2_notch: # double stepping
                self.rotor2_pos = (self.rotor2_pos + 1) % 26
                self.rotor1_pos = (self.rotor1_pos + 1) % 26
            elif self.rotor3_pos == self.rotor3_notch:
                self.rotor2_pos = (self.rotor2_pos + 1) % 26
            self.rotor3_pos = (self.rotor3_pos + 1) % 26
    
    
    def lock(self):
        self.locked = True

    
    def unlock(self):
        self.locked = False


def find_next(x: str, y: str, current: str, target: str, history: set):
    all = []
    for i in range(len(x)):
        if x[i] == current and i not in history:
            if y[i] == target:
                all.append([i])
            else:
                new_history = history.copy()
                new_history.add(i)
                res = find_next(x, y, y[i], target, new_history)
                for item in res:
                    new_item = [i]
                    new_item.extend(item.copy())
                    all.append(new_item)
        elif y[i] == current and i not in history:
            if x[i] == target:
                all.append([i])
            else:
                new_history = history.copy()
                new_history.add(i)
                res = find_next(x, y, x[i], target, new_history)
                for item in res:
                    new_item = [i]
                    new_item.extend(item.copy())
                    all.append(new_item)
    return all
 

def find_cycles(x: str, y: str):
    all = {}
    for i in range(len(x)):
        res = find_next(x, y, y[i], x[i], set([i]))
        for item in res:
            cycle = [i]
            cycle.extend(item.copy())
            if x[i] not in all.keys():
                all[x[i]] = [cycle]
            else:
                all[x[i]].append(cycle)
        res = find_next(x, y, x[i], y[i], set([i]))
        for item in res:
            cycle = [i]
            cycle.extend(item.copy())
            if y[i] not in all.keys():
                all[y[i]] = [cycle]
            else:
                all[y[i]].append(cycle)
    return all


def valid(enigma: Enigma, keyboard_input):

    verbose('ring offsets:', enigma.ring_settings)
    verbose('init position:', enigma.init_settings)
    print('validating. input:', keyboard_input)
    verbose('encryption steps:')

    output = ''
    for c in keyboard_input:
        output += enigma.step(c)
        print('💡' + output[-1])
    
    verbose('-----------------------------')
    verbose('output:', output)
    return output



def test(enigma: Enigma, cycles: dict, subs: dict):
    c, cycle_list = cycles.popitem()
    possible_sc = []
    res = []
    if c in subs.keys():
        possible_sc = [subs[c]]
    else:
        for x in alphabet:
            if x not in subs.keys():
                possible_sc.append(x)
    for sc in possible_sc:
        flag = False
        for cycle in cycle_list:
            current = sc
            for i in cycle:
                enigma.reset()
                enigma.step_for(i)
                current = enigma.step(current)
            if current != sc:
                flag = False
                break
            flag = True
        if flag:
            new_subs = subs.copy()
            new_subs[c] = sc
            new_subs[sc] = c
            if len(cycles.keys()) == 0:
                res.append(new_subs)
            else:
                res.extend(test(enigma, cycles.copy(), new_subs))
    return res


def get_plugboard(subs: dict):
    pb = list(alphabet)
    for c in subs.keys():
        pb[dict26[c]] = subs[c]
    return ''.join(pb)


def main():

    rotor = ['ekmflgdqvzntowyhxuspaibrcj', 'ajdksiruxblhwtmcqgznpyfvoe', 'bdfhjlcprtxvznyeiwgakmusqo']
    notch = ['q', 'e', 'v']
    reflector = 'yruhqsldpxngokmiebfzcwvjat'
    plugboard = 'awcdeighfjolmnkyursvqtbxpz'

    print("crack enigma using alan turing's method.")
    
    known_init_settings = ['a', 'a', 'a']
    known_x = 'bhuilopalopbjxfce'
    known_y = 'pbdppxjomexlfolga'
    print('known init rotor positions:', known_init_settings)
    print('known text:', known_x)
    print('known corresponding cipher:', known_y)

    print('start finding cycles in text-cipher pair...')
    cycles = find_cycles(known_x, known_y)
    print('all found cycles are:', cycles)

    print('start cracking...')

    possible_keys = []
    cnt = 0
    key_space_size = 6 * 26 ** 3
    for p in itertools.permutations([0, 1, 2], 3):
        rotors = [rotor[p[0]], rotor[p[1]], rotor[p[2]]]
        notches = [notch[p[0]], notch[p[1]], notch[p[2]]]
        
        for ring_settings in itertools.product(alphabet, alphabet, alphabet):
            enigma = Enigma(reflector, rotors, notches, ring_settings, known_init_settings)
            subs_list = test(enigma, cycles.copy(), {})
            if len(subs_list) > 0:
                possible_keys.append((p, ring_settings, subs_list))
            cnt += 1
            if cnt % 5000 == 0:
                print(cnt, 'combinations tested, found', len(possible_keys), 'possible keys. rate of progress: {:.2%}'.format(cnt / key_space_size))
    print('all possible keys are:', possible_keys)
    
    best_similarity = -1
    best = None
    for key in possible_keys:
        print('using key', key[0], key[1], 'to decrypt cipher:', known_y)
        rotors = [rotor[key[0][0]], rotor[key[0][1]], rotor[key[0][2]]]
        notches = [notch[key[0][0]], notch[key[0][1]], notch[key[0][2]]]
        ring_offsets = list(key[1])
        for sub in key[2]:
            plugboard = get_plugboard(sub)
            print('trying plugboard', plugboard)
            enigma = Enigma(reflector, rotors, notches, ring_offsets, known_init_settings, plugboard)
            output = valid(enigma, known_y)
            similarity = 0
            for i in range(len(output)):
                if output[i] == known_x[i]:
                    similarity += 1
            print('similarity score is', similarity)
            if similarity > best_similarity:
                best_similarity = similarity
                best = (key[0], key[1], plugboard)
                print('this is by far the most possible one.')
    
    print('cracked key is', best[0], best[1])
    print('putative plugboard is', best[2])


if __name__ == '__main__':
    main()
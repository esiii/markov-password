import math
import pickle
import random
import time


starttime = time.time()

total_level = int(input("please enter the value of total_level (e.g:1000)max_value=1500: "))#1000
threshold_level = int(input("please enter the value of threshold_level (e.g: 10)max_value<total_level: "))#10
total_length = int(input("Please enter the maximum length of the generated password (e.g:13): "))#13

max_ngrams = 1

with open('./{}-gram.pickle'.format(max_ngrams),'rb') as file:
    alphabet = pickle.load(file)


no_alphabet = []
for _ in alphabet:
    for __ in alphabet[_]:
        if __ in alphabet:
            pass
        else:
          no_alphabet.append(__)
no_alphabet = list(set(no_alphabet))
for _ in no_alphabet:
    if _ in alphabet:
        pass
    else:
        alphabet[_]={'å':1}
alphabet['å'] = {'å':1}

# 返回的不仅是mu，而应该是一个level
def mu_level(prev_char, char):
    # print(prev_char, char, normalize(abs(math.log2(alphabet[prev_char][char]))))
    return normalize(abs(math.log2(alphabet[prev_char][char])))


# 遍历所有keyspace，生成所有total length 长度password的出现概率
# 但是这个计算是非常慢的（在大字典的情况下）
# 所以后面再提供一个比较粗暴的估计方法估计最大mu值
# def get_all_prob(current_length=0, prev_char='Ω', current_char=''):
#     global total_length, alphabet
#     if current_length == total_length:
#         return [alphabet[prev_char][current_char]]
#     probs = []
#     current_prob = alphabet[prev_char][current_char] if current_char else 1  # current_char为空意味着是第一个，所以累乘值为100%
#     for char in alphabet[current_char]:
#         probs.extend(get_all_prob(current_length + 1, current_char, char))
#     return [current_prob * prob for prob in probs]


# 粗暴的方法，每一次都取最小，但是这样找到的不一定是最小，所以在normalize的时候把超过的都要另外处理一下
def get_min_prob():
    global total_length, alphabet
    prob = 1
    prev_char = 'Ω'
    for _ in range(total_length):
        prob *= min(alphabet[prev_char].values())
        prev_char = min(alphabet[prev_char], key=alphabet[prev_char].get)
    return prob


def get_range():
    global total_length, alphabet
    max_prob = max([prob for key in alphabet for prob in alphabet[key].values()])
    min_mu_value = abs(math.log2(max_prob))
    # 比较粗暴的方法,找所有单项概率最小的，然后累乘current_length大小
    min_prob = get_min_prob()
    # 比较精确但是要遍历一遍key space的做法：
    # min_prob = min(get_all_prob())
    max_mu_value = abs(math.log2(min_prob)) * total_length
    return min_mu_value, max_mu_value


min_mu_value, max_mu_value = get_range()

#把计算得到的数字数据映射到0~1000
def normalize(mu_value, level_size=total_level):
    global min_mu_value, max_mu_value
    # 向下取整
    return math.floor((mu_value - min_mu_value) / (max_mu_value - min_mu_value) * (level_size - 1))


# tables对应从1到total_length的所有partial table
# 这个表的意思是，在前一个字符是pre_char的情况下，再生成length长度的字符串可以有几个，按照对应的level保存
size_tables = []
for i_length in range(0, total_length):
    size_tables.append({})
    for key in alphabet.keys():
        size_tables[i_length][key] = [0 for _ in range(total_level)]


init_flag = False
def partial_size_fast(partial_length):
    global size_tables, threshold_level
    if partial_length == 1:
        for _prev_char in alphabet:
            for char in alphabet[_prev_char]:
                new_level = mu_level(_prev_char, char)
                size_tables[0][_prev_char][new_level] += 1
    else:
        for prev_char in alphabet:
            #对每一个prec_char的后续都计算累加
            for char in alphabet[prev_char]:
                # 当前的level
                level = mu_level(prev_char, char)
                # 限制不超过最大level
                for _level in range(0, threshold_level - level):
                    # 修改的是当前level加上子串level的那个level对应的size
                    size_tables[partial_length - 1][prev_char][_level + level] += size_tables[partial_length - 2][char][_level]

def auto_partial_size():
    global total_length
    for i in range(total_length):
        partial_size_fast(i + 1)


def get_keyspace():
    global size_tables
    sum_result = 0
    table = size_tables[-1]
    for _ in table['Ω']:
        sum_result += _
    return sum_result

def get_size(dic, key, level = total_level):
    s = 0
    for i in dic[key][:level]:
        s += i
    return s

def get_key_fast(index, remain_length, prev_char='Ω', remain_level = threshold_level):
    global size_tables
    if remain_level < 0:
        return ""
    cursor = 0
    #print("=>", remain_length, prev_char, index, remain_level)
    if remain_length == 1:
        # 枚举所有可能性直到找到
        for char in alphabet[prev_char]:
            dec_level = mu_level(prev_char, char)
            #print(remain_level - dec_level, cursor, char)
            if remain_level - dec_level < 0:
                continue
            if cursor == index :
                return char
            else:
                cursor += 1
        #如果遍历了所有的char还没有找到的话，说明原来是超过了threshold的，就回溯
        else:
            return ''
    else:
        # 记录前面的char的size总和
        cursor = 0
        for char in alphabet[prev_char]:
            # 计算取了当前char之后的level损耗
            dec_level = mu_level(prev_char, char)
            # 记录remian_level下，满足条件的char的size总和
            # remian_legth - 1是当前length的table（因为从0开始的），-2是下一级
            size = get_size(size_tables[remain_length - 2], char, remain_level-dec_level)
            #print(char, size)
            # 如果当前size超过了index，说明是这个char
            if cursor + size > index:
                sub_char = get_key_fast(index - cursor, remain_length - 1, char, remain_level - dec_level)
                if sub_char:
                    return char + sub_char
            else:
                cursor += size
        else:
            if prev_char == 'Ω':
                print("index out of range.")
            else:
                return ""

outputfile = input("Please enter the storage path of the output file (e.g: C:/data/markov-passwd.txt): ")

result_file =  open(outputfile,'w')
if __name__ == "__main__":
    print("initing table")
    auto_partial_size()
    print("table init finished")
    passwd_space = get_keyspace()
    print("Total password space:{}".format(passwd_space))
    passwd_num = int(input("Please enter the number of generate passwords (Less than total password space): "))
    for i in (random.sample(range(0,passwd_space),passwd_num)):
        #test_index = random.randint(0, passwd_space)
        test_index = i
        res = get_key_fast(test_index, total_length)
        res_2 = res.replace('å','')
        result_file.write(res_2)

 

endtime = time.time()
print("Comusing time: %f" % (endtime - starttime))

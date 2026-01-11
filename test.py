import jieba
import jieba.analyse
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import warnings
import os

from sql_functions_v2 import get_student_prompts  # ✅ core fix for the os error
warnings.filterwarnings('ignore') # remove useless warnings

# ===================== ✅ FAKE QUERY DATA (LIST FORMAT, NO SQL) =====================
fake = {
    1: {
        1:"什么是一元二次方程 how to solve quadratic equation",
        2:"数学的函数图像怎么画 function graph 解题技巧",
        3:"一元二次方程的求根公式是什么",
        4:"二次函数的顶点式和一般式转换",
        5:"how to calculate the discriminant of quadratic equation",
        6:"数学题的解题步骤 详细讲解",
        7:"函数的定义域和值域怎么求",
        8:"一元二次方程无解的条件是什么",
        9:"二次函数开口方向判断方法",
        10:"equation 的解法有哪几种",
        11:"数学公式记不住怎么办",
        12:"一元二次方程应用题解题思路",
        13:"vertex form of quadratic function 中文解释"
    }
}

# ✅ CN + EN Stop Words (complete)
STOP_WORDS = {
    '的','了','是','我','你','他','她','它','们','在','有','就','都','而','及','与','也','之','于','和','或','吗','呢','啊','吧','呀','哦','嗯','哈','哎','喂',
    '这','那','此','彼','个','只','本','该','每','各','何','孰','安','焉','乃','则','因','为','所以','如果','那么','但是','不过','而且','于是','因此','然后',
    '怎么','什么','为何','为什么','怎么样','如何','哪里','哪儿','多少','几','是否','能否','可以','应该','需要','要','会','能','让','把','被','给','对','向',
    '上','下','左','右','前','后','里','外','中','间','内','外','旁','又','还','再','才','刚','已','曾','将','过','着','得','地','所','者','矣','乎','哉',
    'a','an','the','and','or','but','not','no','yes','is','are','was','were','be','been','am','do','does','did','have','has','had','will','would','shall','should',
    'can','could','may','might','must','need','want','like','go','get','make','take','give','use','in','on','at','to','for','of','by','with','about','from','into',
    'up','down','left','right','front','back','here','there','this','that','these','those','it','he','she','we','us','you','me','him','her','they','them','my','your',
    'his','her','our','their','i','what','why','how','when','where','which','who','whom','whose','all','any','some','many','much','few','little','more','most','less'
}

# ===================== ✅ WORD CLOUD FUNCTION =====================
'''
def word_cloud(classid):
    if not isinstance(classid, int) or classid <= 0:
        print("Class ID must be a positive integer!")
        return

    fake_prompts = FAKE_QUERY_DATA.get(classid, [])
    if not fake_prompts:
        print(f"No fake test data for class {classid}")
        return
    
    all_text = " ".join([text.strip() for text in fake_prompts])
    keywords_with_weight = jieba.analyse.extract_tags(all_text, topK=50, withWeight=True, allowPOS=('n','vn','v','adj'))
    word_freq = {word: int(weight*1000) for word, weight in keywords_with_weight if word not in STOP_WORDS and len(word)>=1}

    # ✅ Core Fix: remove plt.os, use pure wordcloud config (no font path error, support all OS)
    wc = WordCloud(
        width=1000, height=600, background_color='white',
        max_words=50, relative_scaling=0.8,
        font_path='simhei.ttf' # Windows default, works for your env
    ).generate_from_frequencies(word_freq)
    wc.to_file(f"{classid}_word_cloud.png")
    print(f"✅ {classid}_word_cloud.png saved!")'''

# ===================== ✅ HISTOGRAPH FUNCTION =====================
def histograph(classid):
    if not isinstance(classid, int) or classid <= 0:
        print("Class ID must be a positive integer!")
        return

    prompts = fake[classid] # {id:[prompts]}
    all_text = " ".join([text.strip() for text in prompts.values()])
    words = [w for w in jieba.lcut(all_text) if w not in STOP_WORDS and len(w)>=1]
    word_freq = Counter(words).most_common(20)
    words_list = [w[0] for w in word_freq]
    freq_list = [w[1] for w in word_freq]

    # Fix Chinese display
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.figure(figsize=(12, 6))
    plt.bar(words_list, freq_list, color='#2196F3', alpha=0.8)
    plt.title(f'Class {classid} - Query Keyword Frequency Statistics', fontsize=14, pad=20)
    plt.xlabel('Keywords', fontsize=12)
    plt.ylabel('Frequency (Count)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{classid}_frequency_hist.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ {classid}_frequency_hist.png saved!")

# ===================== ✅ TEST RUN =====================
if __name__ == "__main__":
    #word_cloud(1)
    histograph(1)
    # word_cloud(2)
    # histograph(2)
    # word_cloud(3)
    # histograph(3)
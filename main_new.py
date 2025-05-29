from flask import Flask, render_template, url_for, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import logging
from database_manager import db_manager

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
# 使用环境变量设置密钥，生产环境更安全
app.secret_key = os.environ.get('SECRET_KEY', 'your_very_secret_key_for_session_management')

# 获取端口配置，适配云平台部署
PORT = int(os.environ.get('PORT', 5000))

ALL_QUESTION_DATA_PYTHON = [
    # --- Document 导论.doc (doc_order: 0) ---
    # Single Choice (单项选择题)
    {"id": "导论_s1", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 1, "question": "1.(  )通过了关于《中国共产党章程（修正案）》的决议，把习近平新时代中国特色社会主义思想写入党章。", "options": {"A":"党的十七大", "B":"党的十八大", "C":"党的十九大", "D":"党的二十大"}, "answer": "C"}, # [cite: 52]
    {"id": "导论_s2", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 2, "question": "2.（  ）是改革开放以来我们党全部理论和实践的鲜明主题。", "options": {"A":"贯彻新发展理念", "B":"坚持和发展中国特色社会主义", "C":"改革开放", "D":"以经济建设为中心"}, "answer": "B"}, # [cite: 52]
    {"id": "导论_s3", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 3, "question": "3.党的二十大提出了（   ）。", "options": {"A":"“六个必须坚持”", "B":"“十个明确”", "C":"“十四个坚持”", "D":"“十三个方面成就”"}, "answer": "A"}, # [cite: 52]
    {"id": "导论_s4", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 4, "question": "4. 中国特色社会主义最本质的特征是（   ）。", "options": {"A":"人民共同富裕", "B":"人民当家作主", "C":"中国共产党领导", "D":"社会主义现代化"}, "answer": "C"}, # [cite: 52, 53]
    {"id": "导论_s5", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 5, "question": "5.坚持和发展中国特色社会主义，总任务是（   ）。", "options": {"A":"完善和发展中国特色社会主义制度、推进国家治理体系和治理能力现代化", "B":"建设中国特色社会主义法治体系、建设社会主义法治国家", "C":"实现社会主义现代化和中华民族伟大复兴，在全面建成小康社会的基础上，分两步走在本世纪中叶建成富强民主文明和谐美丽的社会主义现代化强国", "D":"建设一支听党指挥、能打胜仗、作风优良的人民军队，把人民军队建设成为世界一流军队"}, "answer": "C"}, # [cite: 53]
    {"id": "导论_s6", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 6, "question": "6.全面深化改革的总目标是（   ）。", "options": {"A":"坚定道路自信、理论自信、制度自信、文化自信", "B":"完善和发展中国特色社会主义制度、推进国家治理体系和治理能力现代化", "C":"建设中国特色社会主义法治体系、建设社会主义法治国家", "D":"坚持和发展中国特色社会主义"}, "answer": "B"}, # [cite: 53]
    {"id": "导论_s7", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 7, "question": "7. 世界未有之大变局正在加速演变。（  ）仍然是时代主题，但是不稳定不确定性更加突出。", "options": {"A":"发展与共享", "B":"和平与融合", "C":"和平与发展", "D":"开放与包容"}, "answer": "C"}, # [cite: 53]
    {"id": "导论_s8", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 8, "question": "8. 中国特色社会主义的战略布局是（  ", "options": {"A":"“十个明确", "B":"“十四个坚持”", "C":"“四个全面", "D":"“五位一体”"}, "answer": "C"}, # [cite: 53]
    {"id": "导论_s9", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 9, "question": "9.中国特色社会主义的总体布局是（   ）。", "options": {"A":"“三位一体", "B":"“四位一体”", "C":"“五位一体", "D":"“六位一体”"}, "answer": "C"}, # [cite: 53]
    {"id": "导论_s10", "type": "single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 10, "question": "10.习近平新时代中国特色社会主义思想内容十分丰富，涵盖改革发展稳定、内政外交国防、治党治国治军等各个领域、各个方面，构成了一个系统完整、逻辑严密、相互贯通的思想理论体系。下面是指导思想层面的表述的是（  。", "options": {"A":"“四个全面“", "B":"“十四个坚持”", "C":"“十个明确”", "D":"“四个伟大”", "E":"“六个必须坚持“"}, "answer": "C"}, # [cite: 53]
    # Multiple Choice (多项选择题) from 导论.doc
    {"id": "导论_m1", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 1, "question": "1.习近平新时代中国特色社会主义思想创立的时代背景是（）。", "options": {"A":"世界百年未有之大变局加速演进", "B":"新时代中国正处于中华民族伟大复兴的关键时期", "C":"我国经济高速度发展", "D":"中国成为世界领导角色"}, "answer": "AB"}, # [cite: 53]
    {"id": "导论_m2", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 2, "question": "2.新时代中国正处于中华民族伟大复兴的关键时期，因为（ ）。", "options": {"A":"我国发展站在了新的历史起点上", "B":"改革面临着许多前所未有的困难和挑战，处于攻坚克难的关键时期", "C":"新时代的中国发生新的历史性变革", "D":"中国式现代化全面推进拓展"}, "answer": "ABCD"}, # [cite: 53]
    {"id": "导论_m3", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 3, "question": "3.习近平总书记为习近平新时代中国特色社会主义思想的创立发挥了决定性作用，（  ）。", "options": {"A":"坚定的政治信仰和朴素的人民情怀，为这一思想注入了强大精神基因", "B":"丰富的文化积淀和良好的哲学素养，为这一思想奠定了深厚的理论底蕴", "C":"艰苦磨练和扎实的从政历练，为这一思想积累了充分的实践养分", "D":"非凡的政治胆略和高超的政治智慧，为这一思想开辟了宽阔视野"}, "answer": "ABCD"}, # [cite: 53]
    {"id": "导论_m4", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 4, "question": "4.习近平新时代中国特色社会主义思想回答了（ ）重大时代课题。", "options": {"A":"新时代坚持和发展什么样的中国特色社会主义、怎样坚持和发展中国特色社会主义", "B":"建设什么样的社会主义现代化强国、怎样建设社会主义现代化强国", "C":"建设什么样的长期执政的马克思主义政党、怎样建设长期执政的马克思主义政党", "D":"建设什么美好的世界。怎样建设美好世界"}, "answer": "ABC"}, # [cite: 53]
    {"id": "导论_m5", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 5, "question": "5.习近平新时代中国特色社会主义思想的主要内容包括（  ）。", "options": {"A":"“六个必须坚持”", "B":"“十个明确”", "C":"“十四个坚持”", "D":"“十三个方面成就”"}, "answer": "ABCD"}, # [cite: 53, 54]
    {"id": "导论_m6", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 6, "question": "6.“十四个坚持”的基本方略，（  ）。", "options": {"A":"涵盖坚持党的领导和“五位一体”总体布局、“四个全面”战略布局", "B":"涵盖国防和军队建设、维护国家安全、对外战略", "C":"是对党的治国理政重大方针政策的最新概括", "D":"是实现“两个一百年”奋斗目标、实现中华民族伟大复兴中国梦的“路线图”和“方法论”。"}, "answer": "ABCD"}, # [cite: 54] # Assuming all options are correct for question 6 as text implies.
    {"id": "导论_m7", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 7, "question": "7.习近平新时代中国特色社会主义思想是当代中国马克思主义、二十一世纪马克思主义，是（   ）的时代精华，实现了马克思主义中国化新的飞跃。", "options": {"A":"中华文化", "B":"中华品格", "C":"中国精神", "D":"中国力量"}, "answer": "AC"}, # [cite: 54]
    {"id": "导论_m8", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 8, "question": "8. 坚持把马克思主义基本原理同（   ）相结合，用马克思主义观察时代、把握时代、引领时代，继续发展当代中国马克思主义、21世纪马克思主义。", "options": {"A":"中国具体实际相结合", "B":"中华优秀传统文化", "C":"中国精神", "D":"民族特色"}, "answer": "AB"}, # [cite: 54]
    {"id": "导论_m9", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 9, "question": "9.中国特色社会主义事业总体布局是“五位一体”、战略布局是“四个全面”，强调坚定（   ）。", "options": {"A":"道路自信", "B":"理论自信", "C":"制度自信", "D":"文化自信"}, "answer": "ABCD"}, # [cite: 54]
    {"id": "导论_m10", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 10, "question": "10.发展是解决我国一切问题的基础和关键，发展必须是科学发展，必须坚定不移贯彻创新（  ）的发展理念。", "options": {"A":"协调", "B":"绿色", "C":"开放", "D":"共享"}, "answer": "ABCD"}, # [cite: 54]
    {"id": "导论_m11", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 11, "question": "11.建设一支（ ），的人民军队，是实现“两个一百年”奋斗目标、实现中华民族伟大复兴的战略支撑。", "options": {"A":"听党指挥", "B":"能打胜仗", "C":"作风优良", "D":"全心全意为人民服务"}, "answer": "ABC"}, # [cite: 54]
    {"id": "导论_m12", "type": "multiple", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 12, "question": "12.“两个确立”形成的依据是（ ）。", "options": {"A":"“两个确立”是中国共产党基于唯物史观两个基本原理所作出的必然选择", "B":"“两个确立”是党的历史经验的总结运用", "C":"“两个确立”是新时代十年实践形成的智慧结晶", "D":"“两个确立”是战胜外部环境变化出现许多新的风险挑战、解决国内许多深层次矛盾和问题的需要"}, "answer": "ABCD"}, # [cite: 54]
    # Judgment (判断题) from 导论.doc
    {"id": "导论_j1", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 1, "question": "1. 新时代新征程，中国共产党的中心任务，就是团结带领全国各族人民全面建成社会主义现代化强国、实现第一个百年奋斗目标。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 55]
    {"id": "导论_j2", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 2, "question": "2.世界面临百年未有之大变局给中华民族伟大复兴带来重大机遇。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 55]
    {"id": "导论_j3", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 3, "question": "3.习近平新时代中国特色社会主义思想是马克思主义中国化的第一次历史性飞跃。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 55]
    {"id": "导论_j4", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 4, "question": "4.习近平新时代中国特色社会主义思想是在把握世界发展大势、应对全球共同挑战、维护人类共同利益的过程中创立并不断丰富发展的。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 55]
    {"id": "导论_j5", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 5, "question": "5.三个重大时代课题，是站在新时代历史节点上向中国共产党人提出的“时代三问”。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 55]
    {"id": "导论_j6", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 6, "question": "6.我们党的历史，就是一部不断推进马克思主义中国化的历史，就是一部不断推进理论创新、进行理论创造的历史。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 55]
    {"id": "导论_j7", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 7, "question": "7.习近平新时代中国特色社会主义思想系统全面、逻辑严密、博大精深。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 55]
    {"id": "导论_j8", "type": "judgment_as_single", "source_doc": "导论.doc", "doc_order": 0, "q_num_in_doc": 8, "question": "8.“三个代表”重要思想是当代中国马克思主义、二十一世纪马克思主义，是中华文化和中国精神的时代精华，实现了马克思主义中国化时代化新的飞跃。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 55]

    # --- Document 09.doc (doc_order: 9) ---
    # Single Choice (单项选择题)
    {"id": "09_s1", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 1, "question": "1.(  )是党领导人民治理国家的基本方式。", "options": {"A":"以人民为中心", "B":"绿色发展", "C":"依法治国", "D":"人民当家作主"}, "answer": "C"}, # [cite: 1, 64]
    {"id": "09_s2", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 2, "question": "2.全面依法治国的唯一正确道路是(   )。", "options": {"A":"中国特色社会主义道路", "B":"中国特色社会主义政治发展道路", "C":"中国特色社会主义法治道路", "D":"中国特色社会主义法制道路"}, "answer": "C"}, # [cite: 1, 64]
    {"id": "09_s3", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 3, "question": "3.全面依法治国的总抓手是(      )。", "options": {"A":"建设中国特色社会主义法治体系，建设社会主义法治国家", "B":"建设中国特色社会主义法治体系", "C":"建设社会主义法治国家", "D":"坚持中国共产党的领导"}, "answer": "B"}, # [cite: 1, 64]
    {"id": "09_s4", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 4, "question": "4.1997年，（   ）确立依法治国为治理国家的基本方略，把建设社会主义法治国家，确定为社会主义现代化建设的重要目标。", "options": {"A":"党的十四大", "B":"党的十五大", "C":"党的十三届四中全会", "D":"党的十六大"}, "answer": "B"}, # [cite: 1, 64]
    {"id": "09_s5", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 5, "question": "5.（     ）是社会主义法治最根本的保证。", "options": {"A":"中国特色社会主义制度", "B":"党的领导", "C":"严密的法治监督体系", "D":"全面深化改革"}, "answer": "B"}, # [cite: 1, 64]
    {"id": "09_s6", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 6, "question": "6.（   ）是中国特色社会主义法治体系的根本制度基础，是全面推进依法治国的根本制度保障。", "options": {"A":"中国特色社会主义制度", "B":"党的领导", "C":"马克思主义指导", "D":"以德治国"}, "answer": "A"}, # [cite: 1, 65]
    {"id": "09_s7", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 7, "question": "7.（   ）是中国特色社会主义的本质要求和重要保障。", "options": {"A":"全面建设社会主义现代化国家", "B":"全面依法治国", "C":"全面深化改革", "D":"全面从严治党"}, "answer": "B"}, # [cite: 2, 65]
    {"id": "09_s8", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 8, "question": "8.全面依法治国的总抓手是(     )。", "options": {"A":"建设中国特色社会主义法治体系，建设社会主义法治国家", "B":"建设中国特色社会主义法治体系", "C":"建设社会主义法治国家", "D":"坚持中国共产党的领导"}, "answer": "B"}, # [cite: 2, 65]
    {"id": "09_s9", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 9, "question": "9.法治监督体系以(      )为重点.", "options": {"A":"约束公权力运行", "B":"思想教育", "C":"制度建设", "D":"少数领导干部"}, "answer": "A"}, # [cite: 2, 66]
    {"id": "09_s10", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 10, "question": "10.（  ）是推进全面依法治国的根本保证。", "options": {"A":"党的领导", "B":"人民当家作主", "C":"社会和谐稳定", "D":"经济社会发展"}, "answer": "A"}, # [cite: 3, 66]
    {"id": "09_s11", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 11, "question": "11.全面依法治国最广泛、最深厚的基础是（   ）。", "options": {"A":"党的领导", "B":"社会稳定", "C":"人民", "D":"社会主义民主"}, "answer": "C"}, # [cite: 3, 66]
    {"id": "09_s12", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 12, "question": "12.全面依法治国的总目标是(   )。", "options": {"A":"建设中国特色社会主义法治体系", "B":"建设中国特色社会主义法治体系，建设社会主义法治国家", "C":"建设社会主义法治国家", "D":"有法可依、有法必依、违法必究、执法必严"}, "answer": "B"}, # [cite: 3, 66]
    {"id": "09_s13", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 13, "question": "13.（    ）是国家治理体系和治理能力的重要依托。", "options": {"A":"法治", "B":"民主", "C":"人民", "D":"党的领导"}, "answer": "A"}, # [cite: 3, 66]
    {"id": "09_s14", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 14, "question": "14.（    ）是司法的灵魂和生命。", "options": {"A":"公平正义", "B":"民主法治", "C":"诚信友善", "D":"社会和谐"}, "answer": "A"}, # [cite: 3, 66]
    {"id": "09_s15", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 15, "question": "15.（   ）既是全面从严治党的重要依据，也是全面依法治国的有力保障。", "options": {"A":"党内法规", "B":"党的纪律条例", "C":"党章", "D":"党的监督机制"}, "answer": "A"}, # [cite: 3, 67]
    {"id": "09_s16", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 16, "question": "16.（   ）是国家根本法，是党和人民意志的集中体现，是国家各种制度和法律法规的总依据。", "options": {"A":"法律总纲", "B":"民法典", "C":"宪法", "D":"诉讼法"}, "answer": "C"}, # [cite: 4, 67]
    {"id": "09_s17", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 17, "question": "17.我们讲坚持依宪治国、依宪执政，就包括坚持宪法确定的（  ）地位不动摇。", "options": {"A":"人民当家作主", "B":"中国共产党领导", "C":"社会主义法治国家", "D":"宪法权威"}, "answer": "B"}, # [cite: 4, 67]
    {"id": "09_s18", "type": "single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 18, "question": "18.建设中国特色社会主义法治体系，必须坚持（     ）先行。", "options": {"A":"守法", "B":"司法", "C":"执法", "D":"立法"}, "answer": "D"}, # [cite: 4, 68]
    # Multiple Choice (多项选择题) from 09.doc
    {"id": "09_m1", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 1, "question": "1.全面依法治国是（   ）。", "options": {"A":"国家治理的一场深刻革命，关系党执政兴国，关系人民幸福安康", "B":"完善和发展中国特色社会主义制度、推进国家治理体系和治理能力现代化的重要方面", "C":"坚持和发展中国特色社会主义的本质要求和重要保障", "D":"“四个全面”战略布局之一"}, "answer": "ABCD"}, # [cite: 5, 68]
    {"id": "09_m2", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 2, "question": "2.中国特色社会主义法治道路的核心要义是(    )。", "options": {"A":"坚持党的领导", "B":"坚持中国特色社会主义制度", "C":"贯彻中国特色社会主义法治理论", "D":"坚持社会主义根本制度"}, "answer": "ABC"}, # [cite: 5, 68]
    {"id": "09_m3", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 3, "question": "3.要坚持（   ）相结合，实现法治和德治相辅相成、相得益彰。", "options": {"A":"依法治国", "B":"协同发展", "C":"全面发展", "D":"以德治国"}, "answer": "AD"}, # [cite: 5, 68]
    {"id": "09_m4", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 4, "question": "4.中国特色社会主义法治道路的核心要义，就是（    ），这充分体现了我国社会主义性质。", "options": {"A":"坚持党的领导", "B":"坚持中国特色社会主义制度", "C":"贯彻中国特色社会主义法治理论", "D":"坚持从中国实际出发"}, "answer": "ABC"}, # [cite: 5, 68]
    {"id": "09_m5", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 5, "question": "5.关于政治和法治的关系，下列说法正确的是(    )。", "options": {"A":"法治要脱离政治的影响，才能确保公平正义", "B":"法治当中有政治，没有脱离政治的法治", "C":"政治和法治相互依存，相互作用，密不可分", "D":"党和法的关系是政治和法治关系的集中反映"}, "answer": "BCD"}, # [cite: 5, 68]
    {"id": "09_m6", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 6, "question": "6.走中国特色社会主义法治道路，必须长期坚持以下哪些基本原则。（ ）", "options": {"A":"坚持中国共产党的领导", "B":"坚持人民主体地位", "C":"坚持法律面前人人平等", "D":"坚持依法治国与以德治国相结合", "E":"从中国实际出发，"}, "answer": "ABCDE"}, # [cite: 5, 69]
    {"id": "09_m7", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 7, "question": "7.全面依法治国必须正确处理(     )的关系。", "options": {"A":"政治和法治", "B":"改革和法治", "C":"依法治国和以德治国", "D":"依法治国和依规治党"}, "answer": "ABCD"}, # [cite: 6, 69]
    {"id": "09_m8", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 8, "question": "8.正确处理改革和法治的关系 ,要做到（  ）。", "options": {"A":"要坚持改革决策和立法决策相统一", "B":"立法主动适应改革需要，重大改革于法有据", "C":"对实践证明已经比较成熟的改革经验和行之有效的改革举措，要尽快上升为法律。", "D":"对实践条件还不成熟、需要先行先试的，要按照法定程序作出授权", "E":"对不适应改革要求的现行法律法规，要及时修改或废止"}, "answer": "ABCDE"}, # [cite: 6, 69]
    {"id": "09_m9", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 9, "question": "9.正确处理依法治国和依规治党的关系, 要做到（    ）。", "options": {"A":"要发挥依法治国和依规治党的互补性作用,确保党既依据宪法法律治国理政，又依据党内法规管党治党", "B":"要正确处理党的政策和国家法律的关系，两者都是人民根本意志的反映", "C":"党的政策是国家法律的先导和指引", "D":"要通过法律保障党的政策有效实施"}, "answer": "ABCD"}, # [cite: 6, 69]
    {"id": "09_m10", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 10, "question": "10.坚持依宪治国、依宪执政，就必须(    )。", "options": {"A":"坚持宪法确定的中国共产党领导地位不动摇", "B":"坚持宪法确定的人民民主专政的国体和人民代表大会的政体不动摇", "C":"坚持走“宪政”道路不动摇", "D":"学习西方“三权鼎立”制度"}, "answer": "AB"}, # [cite: 6, 69]
    {"id": "09_m11", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 11, "question": "11.更好推进中国特色社会主义法治体系建设，必须加快形成（  ），形成( )。", "options": {"A":"完备的法律规范体系", "B":"高效的法治实施体系", "C":"严密的法治监督体系", "D":"有力的法治保障体系", "E":"完善的党内法规体系"}, "answer": "ABCDE"}, # [cite: 6, 69]
    {"id": "09_m12", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 12, "question": "12.加快形成完备的法律规范体系,必须(  )。", "options": {"A":"深入推进科学立法、民主立法、依法立法，统筹立改废释纂", "B":"提高立法效率，增强立法系统性、整体性、协同性和时效性。", "C":"研究丰富立法形式，增强立法的针对性、适用性、可操作性。", "D":"推进合宪性审査工作"}, "answer": "ABCD"}, # [cite: 6, 69]
    {"id": "09_m13", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 13, "question": "13.准确把握全面推进依法治国重点任务，着力推进（   ）。", "options": {"A":"科学立法", "B":"严格执法", "C":"公正司法", "D":"全民守法"}, "answer": "ABCD"}, # [cite: 6, 69]
    {"id": "09_m14", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 14, "question": "14.坚持以宪法为最高法律规范，完善以宪法为核心的中国特色社会主义法律体系，加强（   ）立法，把国家各项事业和各项工作纳入法制轨道。", "options": {"A":"重点领域", "B":"突出领域", "C":"新兴领域", "D":"涉外领域"}, "answer": "ACD"}, # [cite: 6, 70]
    {"id": "09_m15", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 15, "question": "15.法治中国建设的总体目标是（  ）。", "options": {"A":"到2025年，党领导全面依法治国体制机制更加健全，以宪法为核心的中国特色社会主义法律体系更加完备", "B":"到2025年，法治社会建设取得重大进展，党内法规体系更加完善", "C":"到2025年，中国特色社会主义法治体系初步形成", "D":"到2035年，法治国家、法治政府、法治社会基本建成"}, "answer": "ABCD"}, # [cite: 7, 70]
    {"id": "09_m16", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 16, "question": "16.法治中国建设的工作布局是（  ）。", "options": {"A":"坚持依法治国、依法执政、依法行政共同推进", "B":"坚持法治国家、法治政府、法治社会一体建设", "C":"坚持统筹推进国内法治和涉外法治", "D":"协商民主和法制宣传一体推进"}, "answer": "ABC"}, # [cite: 7, 70]
    {"id": "09_m17", "type": "multiple", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 17, "question": "17.建设更高水平的法治中国，必须（    ）。", "options": {"A":"完善以宪法为核心的中国特色社会主义法律体系", "B":"扎实推进依法行政", "C":"严格公正司法", "D":"加快建设法治社会"}, "answer": "ABCD"}, # [cite: 7, 70]
    # Judgment (判断题) from 09.doc
    {"id": "09_j1", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 1, "question": "1.党的领导和社会主义法治是一致的，社会主义法治必须坚持党的领导，党的领导必须依靠社会主义法治。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 7, 70]
    {"id": "09_j2", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 2, "question": "2.中国特色社会主义法治道路是社会主义法治建设成就和经验的集中体现，是建设社会主义法治国家的唯一正确道路。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 7, 70]
    {"id": "09_j3", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 3, "question": "3.“立善法于天下，则天下治；立善法于一国，则一国治。”全面依法治国，必须加快完善中国特色社会主义法律体系，使之更加科学完备、统一权威。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 7, 70]
    {"id": "09_j4", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 4, "question": "4. 我们讲依宪治国、依宪执政，同西方所谓“宪政”有着本质区别，不能把二者混为一谈。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 7, 71]
    {"id": "09_j5", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 5, "question": "5.坚持依法执政首先要坚持依宪执政。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 8, 71]
    {"id": "09_j6", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 6, "question": "6.建设中国特色社会主义法治体系、建设社会主义法治国家是实现国家治理体系和治理能力现代化的必然要求，也是全面深化改革的必然要求，有利于在法治轨道上推进国家治理体系和治理能力现代化。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 8, 71]
    {"id": "09_j7", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 7, "question": "7.法治可以脱离一定社会经济、政治和文化所提供的社会条件。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 8, 71]
    {"id": "09_j8", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 8, "question": "8.依法治国是党领导人民治理国家的基本方式。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 8, 71]
    {"id": "09_j9", "type": "judgment_as_single", "source_doc": "09.doc", "doc_order": 9, "q_num_in_doc": 9, "question": "9.法治是是制度之治最基本最稳定最可靠的保障。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 8, 71]

    # --- Document 10.doc (doc_order: 10) ---
    # Single Choice (单项选择题)
    {"id": "10_s1", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 1, "question": "1.建设社会主义文化强国、推动社会主义文化繁荣兴盛，关键在于（）。", "options": {"A":"坚定中国特色社会主义文化自信", "B":"高质量发展", "C":"提高综合国力", "D":"贯彻新发展理念"}, "answer": "A"}, # [cite: 9, 72]
    {"id": "10_s2", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 2, "question": "2.坚持马克思主义在意识形态领域指导地位的制度是中国特色社会主义制度体系的一项（  ）。", "options": {"A":"基本制度", "B":"根本制度", "C":"重要制度", "D":"基本政策"}, "answer": "B"}, # [cite: 9, 72]
    {"id": "10_s3", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 3, "question": "3.建设中国特色社会主义文化，必须牢牢掌握(   ).", "options": {"A":"马克思主义的科学理论", "B":"网络空间的治理和引导", "C":"意识形态工作领导权", "D":"中国特色社会主义科学体系的构建"}, "answer": "C"}, # [cite: 9, 73]
    {"id": "10_s4", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 4, "question": "4.培育和践行社会主义核心价值观，要把(   )融入社会生活各个方面。", "options": {"A":"社会主义核心价值体系", "B":"理想信念、价值理念、道德观念", "C":"中华优秀传统文化", "D":"社会主义核心价值观"}, "answer": "D"}, # [cite: 10, 73]
    {"id": "10_s5", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 5, "question": "5.(   )是一个民族赖以维系的精神纽带，是一个国家共同的思想道德基础。", "options": {"A":"社会主义核心价值观", "B":"核心价值观", "C":"理想信念", "D":"社会主义核心价值体系"}, "answer": "B"}, # [cite: 10, 73]
    {"id": "10_s6", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 6, "question": "6.建设社会主义文化强国，必须培养高度的(   )。", "options": {"A":"文化自觉", "B":"文化自信", "C":"文化创造活力", "D":"文化软实力"}, "answer": "B"}, # [cite: 10, 73]
    {"id": "10_s7", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 7, "question": "7.构建中国特色哲学社会科学，是掌握意识形态工作领导权的内在要求，首要的是(   )。", "options": {"A":"旗帜鲜明坚持以马克思主义为指导，深化马克思主义理论研究和建设", "B":"在学科体系、学术体系等方面体现中国特色、中国风格、中国气派", "C":"建设中国特色新型智库", "D":"拒绝一切来自西方哲学社会科学的影响"}, "answer": "A"}, # [cite: 10, 73]
    {"id": "10_s8", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 8, "question": "8.下列观点和认识中，错误的是 (    )。", "options": {"A":"当今时代，文化在综合国力竞争中的地位日益重要，谁占据了文化发展的制高点，谁就能够更好地在激烈的国际竞争中掌握主动权", "B":"文化强国既表现为具有高度文化素养的国民，也表现为发达的文化产业，还表现为强大的文化软实力", "C":"文化自信是一个国家、一个民族发展中更基本、更深沉、更持久的力量。坚定文化自信，事关文化安全，事关民族精神的独立性", "D":"文化是一种跨越国界、跨越民族、跨越时空的普适性精神力量，因此，要积极融入世界文化，完全没有必要坚守中华文化立场、走中国特色社会主义文化发展道路"}, "answer": "D"}, # [cite: 10, 73]
    {"id": "10_s9", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 9, "question": "9.（   ）是更基础、更广泛、更深厚的自信，是一个国家、一个民族发展中最基本、最深沉、最持久的力量。", "options": {"A":"文化自信", "B":"文化自觉", "C":"文化软实力", "D":"中国特色社会主义文化"}, "answer": "A"}, # [cite: 10, 74]
    {"id": "10_s10", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 10, "question": "10.一个国家、一个民族的强盛，总是以文化兴盛为支撑的，中华民族伟大复兴需要以（    ）发展繁荣为条件。", "options": {"A":"社会主义经济", "B":"社会主义制度", "C":"中华文化", "D":"社会主义文化"}, "answer": "C"}, # [cite: 11, 74]
    {"id": "10_s11", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 11, "question": "11.(   )是担负文化使命、实现中华民族伟大复兴的根本保证。", "options": {"A":"党的领导", "B":"文化发展繁荣", "C":"文化自信", "D":"科学的民族的大众的文化"}, "answer": "A"}, # [cite: 11, 74]
    {"id": "10_s12", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 12, "question": "12.(   )是当代中国文化发展的灵魂。", "options": {"A":"社会主义", "B":"马克思主义", "C":"中国特色社会主义", "D":"中华优秀传统文化"}, "answer": "B"}, # [cite: 11, 74]
    {"id": "10_s13", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 13, "question": "13.(   )提出社会主义核心价值观。", "options": {"A":"党的十七大", "B":"党的十八大", "C":"党的十九大", "D":"党的二十大"}, "answer": "B"}, # [cite: 11, 74]
    {"id": "10_s14", "type": "single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 14, "question": "14.(   )是中华文明的智慧结晶和精华所在，是中华民族的根和魂，是我们在世界文化激荡中站稳脚跟的根基。", "options": {"A":"中华优秀传统文化", "B":"社会主义先进文化", "C":"革命文化号", "D":"中国特色社会主义文化"}, "answer": "A"}, # [cite: 11, 74]
    # Multiple Choice (多项选择题) from 10.doc
    {"id": "10_m1", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 1, "question": "1.文化繁荣兴盛是（  ）。", "options": {"A":"实现中华民族伟大复兴的必然要求", "B":"建设社会主义现代化强国的应有之义", "C":"满足人民日益增长的美好生活需要的内在要求", "D":"在世界文化激荡中站稳脚跟的基础"}, "answer": "ABCD"}, # [cite: 11, 74]
    {"id": "10_m2", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 2, "question": "2.坚定中国特色社会主义文化自信的底气来自（   ）。", "options": {"A":"中华优秀传统文化，这是我们坚定文化自信的深厚基础", "B":"马克思主义指导下形成的革命文化和社会主义先进文化。这是我们坚定文化自信的根本所在", "C":"中国特色社会主义的伟大实践。这是我们坚定文化自信的不竭源泉", "D":"世界各国文明的交流互鉴"}, "answer": "ABC"}, # [cite: 11, 74]
    {"id": "10_m3", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 3, "question": "3.必须坚持中国特色社会主义文化发展道路，增强文化自信，必须（ ）。", "options": {"A":"围绕举旗帜、聚民心、育新人、兴文化、展形象建设社会主义文化强国", "B":"发展面向现代化、面向世界、面向未来的，民族的科学的大众的社会主义文化", "C":"激发全民族文化创新创造活力，增强实现中华民族伟大复兴的精神力量", "D":"以马克思主义为指导，坚守中华文化立场"}, "answer": "ABCD"}, # [cite: 11, 74]
    {"id": "10_m4", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 4, "question": "4.坚持举旗帜、聚民心、育新人、兴文化、展形象。举旗帜，就是要（）。", "options": {"A":"高举马克思主义的旗帜", "B":"高举中国特色社会主义的旗帜", "C":"坚持不懈用习近平新时代中国特色社会主义思想武装全党、教育人民", "D":"高举无产阶级专政的旗帜"}, "answer": "ABC"}, # [cite: 11, 75]
    {"id": "10_m5", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 5, "question": "5.坚持中国特色社会主义文化建设的“二为”方向，“二为”是（）。", "options": {"A":"为中国共产党治国理政服务", "B":"为建设社会主义现代化国家", "C":"为人民服务", "D":"为社会主义服务"}, "answer": "CD"}, # [cite: 12, 75]
    {"id": "10_m6", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 6, "question": "6.坚持马克思主义在意识形态领域指导地位的根本制度，必须（ ）。", "options": {"A":"牢牢掌握党对意识形态工作领导权", "B":"坚持以立为本、立破并举，提高政治自觉，把意识形态阵地建设和管理工作摆在重要位置，", "C":"全面落实意识形态工作责任制，压紧压实做好意识形态工作的政治责任。", "D":"要切实把坚持以马克思主义为指导体现到理论武装、舆论引导、思想道德建设、文化文艺等各方面"}, "answer": "ABCD"}, # [cite: 12, 75] # Corrected option B to remove trailing comma
    {"id": "10_m7", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 7, "question": "7.意识形态工作(    )。", "options": {"A":"事关党的前途命运和国家长治久安", "B":"是党的一项极端重要的工作", "C":"是为国家立心、为民族立魂的工作", "D":"事关民族凝聚力和向心力"}, "answer": "ABCD"}, # [cite: 12, 75]
    {"id": "10_m8", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 8, "question": "8.100多年前，中国共产党的先驱们创建了中国共产党,形成了(   )的伟大建党精神。", "options": {"A":"坚持真理、坚守理想", "B":"践行初心、担当使命", "C":"不怕牺牲、英勇斗争", "D":"对党忠诚、不负人民"}, "answer": "ABCD"}, # [cite: 12, 75]
    {"id": "10_m9", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 9, "question": "9.中国共产党人精神谱系（   ）。", "options": {"A":"集中体现了党的坚定信念、根本宗旨、优良作风", "B":"凝聚着中国共产党人艰苦奋斗、牺牲奉献、开拓进取的伟大品格", "C":"已经深深融入党、国家、民族、人民的血脉和灵魂", "D":"成为民族精神和时代精神的重要组成部分。"}, "answer": "ABCD"}, # [cite: 12, 75]
    {"id": "10_m10", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 10, "question": "10.提高全社会文明程度,(   )。", "options": {"A":"是全面建设社会主义现代化国家的重要目标", "B":"是建设社会主义文化强国的重大任务", "C":"要把理想信念教育作为基础性工程", "D":"实施公民道德建设工程", "E":"培育时代新风新貌"}, "answer": "ABCDE"}, # [cite: 12, 75]
    {"id": "10_m11", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 11, "question": "11.对待中华优秀传统文化的态度是（  ）。", "options": {"A":"要坚持马克思主义的立场观点方法，坚持古为今用、推陈出新，有鉴别地加以对待，有扬弃地予以继承", "B":"要坚持创造性转化，对那些仍有借鉴价值的内涵和陈旧的表现形式加以改造，赋予其新的时代内涵", "C":"要坚持创新性发展，就是对中华优秀传统文化的内涵加以补充、拓展、完善，增强其影响力和感召力", "D":"要反对复古主义，也要反对历史虚无主义"}, "answer": "ABCD"}, # [cite: 12, 75]
    {"id": "10_m12", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 12, "question": "12.像爱惜自己的生命一样保护好文化遗产，守护好中华文脉。因为（）。", "options": {"A":"文化遗产承载灿烂文明", "B":"传承历史文化", "C":"维系民族精神", "D":"加强社会主义精神文明建设的深厚滋养"}, "answer": "ABCD"}, # [cite: 12, 76]
    {"id": "10_m13", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 13, "question": "13.提高国家文化软实力，就必须（   ）。", "options": {"A":"使当代中国价值观念走向世界。", "B":"要客观真实向世界讲好中国故事", "C":"全面阐述我国的发展观、文明观、全球治理观", "D":"加强国际传播能力建设", "E":"加快构建中国话语和中国叙事体系"}, "answer": "ABCDE"}, # [cite: 13, 76]
    {"id": "10_m14", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 14, "question": "14.对“意识形态工作是为国家立心、为民族立魂的工作”的理解是（）。", "options": {"A":"意识形态工作事关党的前途命运和国家长治久安", "B":"对马克思主义的信仰和社会主义道路，是中国特色社会主义文化活的灵魂", "C":"坚持以什么思想理论为指导，关系国家的方向，关系民族的命脉", "D":"坚持马克思主义在意识形态领域指导地位的制度是坚持和巩固我国社会主义制度、保证我国文化建设正确方向的必然要求", "E":"意识形态上不安全，必然导致政治上的不安全"}, "answer": "ABCDE"}, # [cite: 13, 76]
    {"id": "10_m15", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 15, "question": "15.社会主义核心价值观涉及国家、社会、公民三个层面的价值要求，具体表达为(   )", "options": {"A":"富强、民主、文明、和谐", "B":"自由、民族、公正、法治", "C":"爱国、敬业、诚信、友善", "D":"自由、平等、公正、法治"}, "answer": "ACD"}, # [cite: 13, 76]
    {"id": "10_m16", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 16, "question": "16.建设社会主义文化强国，必须做到(    )", "options": {"A":"培养高度的文化自信", "B":"提升公共文化服务水平", "C":"健全现代文化产业体系", "D":"提高国家文化软实力"}, "answer": "ABCD"}, # [cite: 13, 76]
    {"id": "10_m17", "type": "multiple", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 17, "question": "17.一个国家的文化软实力，从根本上说，取决于其核心价值观的(   )。", "options": {"A":"生命力", "B":"凝聚力", "C":"感召力", "D":"影响力"}, "answer": "ABC"}, # [cite: 13, 76]
    # Judgment (判断题) from 10.doc
    {"id": "10_j1", "type": "judgment_as_single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 1, "question": "1.中华文明形成了中国人看待世界、看待社会、看待人生的独特价值体系、文化内涵和精神品质，铸就了中华民族博采众长的文化自信。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 14, 77]
    {"id": "10_j2", "type": "judgment_as_single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 2, "question": "2.一个国家、一个民族的强盛，总是以文化兴盛为支撑的。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 14, 77]
    {"id": "10_j3", "type": "judgment_as_single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 3, "question": "3.一个政权的瓦解往往是从思想领域开始的，政治动荡、政权更迭可能在一夜之间发生，思想演化也是转瞬即变。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 14, 77]
    {"id": "10_j4", "type": "judgment_as_single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 4, "question": "4.文化软实力集中体现了一个国家基于文化而具有的凝聚力和生命力，以及由此产生的吸引力和影响力。在一个国家的总体实力中，国家的硬实力固然具有标志性、基础性作用", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 14, 77]
    {"id": "10_j5", "type": "judgment_as_single", "source_doc": "10.doc", "doc_order": 10, "q_num_in_doc": 5, "question": "5.文化的影响力首先是政治立场的影响力。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 14, 77]

        # --- Document 11.doc (doc_order: 11) ---
    # Single Choice (单项选择题)
    {"id": "11_s1", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 1, "question": "1.（   ）是我们坚持立党为公、执政为民的本质要求。", "options": {"A":"增进民生福祉", "B":"建立强大的国防", "C":"全面依法治国", "D":"思想政治教育"}, "answer": "A"}, # [cite: 1]
    {"id": "11_s2", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 2, "question": "2.（  ）是我们一切工作的出发点和落脚点。", "options": {"A":"构建新发展格局", "B":"让老百姓过上好日子", "C":"促进高质量发展", "D":"问题导向"}, "answer": "B"}, # [cite: 1]
    {"id": "11_s3", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 3, "question": "3.（  ）是“国之大者”。", "options": {"A":"人才辈出", "B":"建立强大的军队", "C":"实现社会主义现代化", "D":"让人民生活幸福"}, "answer": "D"}, # [cite: 1]
    {"id": "11_s4", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 4, "question": "4．民生是人民幸福之基、社会和谐之本。带领人民群众创造幸福生活，要顺应人民群众对美好生活的向往，坚持（   ）的发展思想，以（   ）为重点，发展各项社会事业。", "options": {"A":"以经济建设为中心；优先发展教育事业习交流", "B":"以人为本；提高就业质量和人民收入水平", "C":"以人民为中心；保障和改善民生", "D":"以社会和谐为中心；加强社会保障体系建设"}, "answer": "C"}, # [cite: 1]
    {"id": "11_s5", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 5, "question": "5.(  ）是政府联系群众的最终一公里。", "options": {"A":"乡村人民政府", "B":"居委会", "C":"基层党支部", "D":"城乡社区"}, "answer": "D"}, # [cite: 1]
    {"id": "11_s6", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 6, "question": "6．基层治理是国家治理的基石，统筹推进乡镇（街道）和城乡社区治理，是实现（  ）的基础工程。", "options": {"A":"国家治理体系和治理能力现代化", "B":"完善适社会治理方式和治理能力", "C":"中国特色社会主义法详共教课学习交流", "D":"中华民族伟大复兴"}, "answer": "A"}, # [cite: 1, 2]
    {"id": "11_s7", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 7, "question": "7要坚持（ ）为主体，提高劳动报酬在初次分配中的比重，完善按要素分配政策。", "options": {"A":"按生产要素", "B":"按社会制度", "C":"按人民需求", "D":"按劳分配"}, "answer": "D"}, # [cite: 2]
    {"id": "11_s8", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 8, "question": "8．坚持以人民为中心的发展思想，在高质量发展中促进共同富裕，正确处理（）的关系，构建初次分配、再分配、三次分配协调配套的基础性制度安排。", "options": {"A":"效率和公平", "B":"收入和分配", "C":"经济和社会", "D":"政府和市场"}, "answer": "A"}, # [cite: 2]
    {"id": "11_s9", "type": "single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 9, "question": "9.(  ）是最大的民生工程、民心工程、根基工程，是社会稳定的重要保障。", "options": {"A":"生产", "B":"共同富裕", "C":"就业", "D":"生活水平"}, "answer": "C"}, # [cite: 2]
    # Multiple Choice (多项选择题) from 11.doc
    {"id": "11_m1", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 1, "question": "1.增进民生福祉是（      ）。", "options": {"A":"坚持立党为公、执政为民的本质要求", "B":"社会主义生产的根本目的", "C":"全面建设社会主义现代化国家的应有之义", "D":"社会主义和资本主义的根本区别之一"}, "answer": "ABCD"}, # [cite: 2]
    {"id": "11_m2", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 2, "question": "2.在脱贫攻坚战中，推进“五个一批”工程，即（  ）。", "options": {"A":"发展生产脱贫一批", "B":"易地搬迁脱贫一批", "C":"生态补偿脱贫一批", "D":"发展教育脱贫一批", "E":"社会保障兜底一批"}, "answer": "ABCDE"}, # [cite: 2, 3]
    {"id": "11_m3", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 3, "question": "3.在脱贫攻坚战中，稳定实现贫困人口“两不愁三保障”，即（ ）。", "options": {"A":"不愁吃", "B":"不愁穿", "C":"义务教育", "D":"基本医疗", "E":"住房安全有保障。"}, "answer": "ABCDE"}, # [cite: 3]
    {"id": "11_m4", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 4, "question": "4.保障和改善民生的工作思路是(    ）。", "options": {"A":"坚守底线", "B":"突出重点", "C":"完善制度", "D":"引导预期"}, "answer": "ABCD"}, # [cite: 3]
    {"id": "11_m5", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 5, "question": "5.(    )是保障和改善民生的重要方针。", "options": {"A":"尽力而为", "B":"量力而行", "C":"突出重点", "D":"正确把握民生和发展的关系"}, "answer": "AB"}, # [cite:  3]
    {"id": "11_m6", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 6, "question": "6.（   ）是保障和改善民生的重要原则。", "options": {"A":"坚持人人尽责", "B":"人人享有", "C":"完善制度", "D":"实事求是"}, "answer": "AB"}, # [cite: 3]
    {"id": "11_m7", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 7, "question": "7.完善分配制度，要做到（     ）。", "options": {"A":"构建初次分配、再分配、第三次分配协调配套的制度体系。", "B":"努力提高劳动报酬在初次分配中的比重，健全工资合理增长机制", "C":"探索通过土地、资本等要素使用权、收益权增加中低收入群体要素收入", "D":"不断壮大中等收入群体", "E":"加大税收、社保、转移支付等的调节力度"}, "answer": "ABCDE"}, # [cite: 3]
    {"id": "11_m8", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 8, "question": "8.实施就业优先战略,必须（     ）。", "options": {"A":"健全就业公共服务体系", "B":"完善重点群体就业支持体系", "C":"扩大高校毕业生就业渠道", "D":"稳定农民工等重点群体就业", "E":"加强困难群体就业兜底帮扶"}, "answer": "ABCDE"}, # [cite: 3, 4]
    {"id": "11_m9", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 9, "question": "9.中国特色的社会保障体系把(   )作为根本出发点和落脚点，推动社会保障事业不断前进。", "options": {"A":"坚持人民至上", "B":"坚持共同富裕", "C":"增进民生福祉", "D":"促进社会公平"}, "answer": "CD"}, # [cite: 4]
    {"id": "11_m10", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 10, "question": "10.社会保障体系主要涉及（  ）等方面。", "options": {"A":"社会保险", "B":"社会救助", "C":"社会福利", "D":"社会优抚"}, "answer": "ABCD"}, # [cite: 4]
    {"id": "11_m11", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 11, "question": "11.健全和完善社会保障体系是新时代加强社会建设的重要着力点。坚持以(  )为重点，推动我国社会保障体系建设进入快车道。", "options": {"A":"增强公平性", "B":"适应流动性", "C":"保证可持续性", "D":"高质量快速发展"}, "answer": "ABC"}, # [cite: 4]
    {"id": "11_m12", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 12, "question": "12.加强和创新社会治理，就是（   ）。", "options": {"A":"在党的领导下，以政府为主导，以社会多元主体参与为基础", "B":"以维护人民群众根本利益为核心", "C":"通过合作、对话、协商、沟通等方式，依法对社会事务、社会组织和社会生活进行引导和规范，化解社会矛盾", "D":"促进社会公平，推动社会稳定有序发展。"}, "answer": "ABCD"}, # [cite: 4]
    {"id": "11_m13", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 13, "question": "13.加强和创新社会治理，改进社会治理方式，要坚持(     )。", "options": {"A":"系统治理", "B":"依法治理", "C":"综合治理", "D":"源头治理"}, "answer": "ABCD"}, # [cite: 4]
    {"id": "11_m14", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 14, "question": "14.健全社会治理制度,要（   ）。", "options": {"A":"构建源头防控、排查梳理、纠纷化解、应急处置的社会矛盾综合治理机制", "B":"健全公共安全体制机制，编织全方位、立体化的公共安全网", "C":"完善社会治安综合治理体制机制系", "D":"健全社会心理服务体系和疏导机制"}, "answer": "ABCD"}, # [cite: 4]
    {"id": "11_m15", "type": "multiple", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 15, "question": "15.不断创新社会治理方式 .要做到（     ）。", "options": {"A":"正确处理好维稳与维权、活力与秩序的关系", "B":"运用法治思维和法治方式统筹社会力量、平衡社会利益、调节社会关系。", "C":"强化互联网思维，推进政府决策科学化、社会治理精准化、公共服务高效化。", "D":"坚持系统思维，综合运用专业化工作方法提升社会治理效能"}, "answer": "ABCD"}, # [cite: 4, 5]
    # Judgment (判断题) from 11.doc
    {"id": "11_j1", "type": "judgment_as_single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 1, "question": "1.社会建设主要包括两个方面重点：一是提高保障和改善民生水平、二是加强和创新社会治理。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 5]
    {"id": "11_j2", "type": "judgment_as_single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 2, "question": "2.保障和改善民生的重要原则是只要尽力而为，不要量力而行。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 5]
    {"id": "11_j3", "type": "judgment_as_single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 3, "question": "3.推进社会治理现代化的目标是建设人人有责、人人尽责、人人享有的社会治理共同体。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 5]
    {"id": "11_j4", "type": "judgment_as_single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 4, "question": "4.发展是解决民生问题的“总钥匙”，民生是发展的“指南针”。要在发展过程中始终注重民生、保障民生、改善民生。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 5]
    {"id": "11_j5", "type": "judgment_as_single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 5, "question": "5.解决人民群众最关心最直接最现实的利益问题,是保障和改善民生的重中之重。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 5]
    {"id": "11_j6", "type": "judgment_as_single", "source_doc": "11.doc", "doc_order": 11, "q_num_in_doc": 6, "question": "6.人民健康是社会文明进步的基础，是民族昌盛和国家富强的重要标志，是促进人的全面发展的必然要求。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 5]

    # --- Document 12.doc (doc_order: 12) ---
    # Single Choice (单项选择题)
    {"id": "12_s1", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 1, "question": "1.（  ）提出：“要像保护眼睛一样保护生态环境，像对待生命一样对待生态环境，”", "options": {"A":"邓小平", "B":"江泽民", "C":"胡锦涛", "D":"习近平"}, "answer": "D"}, # [cite: 6]
    {"id": "12_s2", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 2, "question": "2.（     ）是工业文明发展到一定阶段的产物。", "options": {"A":"农业文明", "B":"中华文明", "C":"生态文明", "D":"文明交流"}, "answer": "C"}, # [cite: 6]
    {"id": "12_s3", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 3, "question": "3.“天地与我并生，而万物与我为一”的“天人合一”思想，代表着我们祖先对处理（  ）的关系的重要认识。", "options": {"A":"天与地", "B":"人与自然", "C":"人与社会", "D":"人与人"}, "answer": "B"}, # [cite: 6]
    {"id": "12_s4", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 4, "question": "4.处理好绿水青山和金山银山的关系，关键在人，关键在（  ）。", "options": {"A":"效益", "B":"钱", "C":"思路", "D":"高质量发展"}, "answer": "C"}, # [cite: 6, 7]
    {"id": "12_s5", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 5, "question": "5.习近平指出：“（   ）是最公平的公共产品，是最普惠的民生福祉。”", "options": {"A":"一带一路", "B":"法律面前人人平等", "C":"良好的生态环境", "D":"按劳分配"}, "answer": "C"}, # [cite: 7]
    {"id": "12_s6", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 6, "question": "6.（  ）是全面建设社会主义现代化国家的重要目标，也是满足人民日益增长的优美生态环境需要的必然要求。", "options": {"A":"依法治国", "B":"建设美丽中国", "C":"共同富裕", "D":"建设文化强国"}, "answer": "B"}, # [cite: 7]
    {"id": "12_s7", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 7, "question": "7.要树立尊重自然、顺应自然、保护自然的生态文明理念，增强（  ）的意识。", "options": {"A":"金山银山不如绿水青山", "B":"绿水青山就是金山银山", "C":"金山银山就是绿水青山", "D":"绿水青山胜过金山银山"}, "answer": "B"}, # [cite: 7]
    {"id": "12_s8", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 8, "question": "8.加快构建生态文明体系，确保到（  ）美丽中国目标基本实现。", "options": {"A":"2020年", "B":"2025年", "C":"2030年", "D":"2035年"}, "answer": "D"}, # [cite: 7]
    {"id": "12_s9", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 9, "question": "9.人因自然而生，人与自然是一种(    )。", "options": {"A":"利用关系", "B":"共生关系", "C":"敌对关系", "D":"生存关系"}, "answer": "B"}, # [cite: 7]
    {"id": "12_s10", "type": "single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 10, "question": "10.习近平“两山论”的突出贡献是（  ）。", "options": {"A":"马克思主义生产力观的新成果", "B":"马克思主义唯物史观的新成果", "C":"马克思主义文明观的新成果", "D":"马克思主义世界观的新成果"}, "answer": "A"}, # [cite: 7, 8]
    # Multiple Choice (多项选择题) from 12.doc
    {"id": "12_m1", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 1, "question": "1.绿水青山是（    ）。", "options": {"A":"自然财富", "B":"生态财富", "C":"社会财富", "D":"经济财富"}, "answer": "ABCD"}, # [cite: 8]
    {"id": "12_m2", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 2, "question": "2.生态文明建设是（   ）。", "options": {"A":"重大的经济问题", "B":"关系党的使命宗旨的重大政治问题", "C":"关系民生福祉的重大社会问题", "D":"“五位一体”总体布局之一"}, "answer": "ABCD"}, # [cite: 8]
    {"id": "12_m3", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 3, "question": "3.对“绿水青山就是金山银山”的理解，正确的观点是（  ）。", "options": {"A":"这是重要的发展理念", "B":"也是推进现代化建设的重大原则", "C":"阐明了经济发展与生态环境保护之间的关系", "D":"揭示了保护生态环境就是保护生产力、改善生态环境就是发展生产力的道理，", "E":"指明了实现发展和保护协同共生的新路径"}, "answer": "ABCDE"}, # [cite: 8] # Option D had a comma at the end, removed.
    {"id": "12_m4", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 4, "question": "4.生态文明建设战略地位更加凸显,表现在（   ）。", "options": {"A":"把“生态文明建设”纳入“五位一体”总体布局", "B":"把“坚持人与自然和谐共生”纳入新时代坚持和发展中国特色社会主义的基本方略", "C":"把“促进人与自然和谐共生”纳入中国式现代化的本质要求", "D":"把“美丽中国”纳入社会主义现代化强国目标;把“绿色”纳入新发展理念", "E":"党的十九大把“增强绿水青山就是金山银山的意识”等写入党章"}, "answer": "ABCDE"}, # [cite: 8]
    {"id": "12_m5", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 5, "question": "5.加快形成绿色生产方式和生活方式,要（    ）。", "options": {"A":"加快推动产业结构、能源结构、交通运输结构等调整优化", "B":"推进各类资源节约集约利用", "C":"积极稳妥推进碳达峰碳中和", "D":"健全绿色发展的保障体系", "E":"把建设美丽中国转化为全体人民的自觉行动"}, "answer": "ABCDE"}, # [cite: 8]
    {"id": "12_m6", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 6, "question": "6.生态文明制度体系更加健全,表现在(   )。", "options": {"A":"制定出台《中共中央国务院关于加快推进生态文明建设的意见》《生态文明体制改革总体方案》等纲领性文件", "B":"制定数十项涉及生态文明建设的改革方案，生态文明“四梁八柱”性质的制度体系基本形成", "C":"制定修订环境保护法、环境保护税法等30多部生态环境领域法律和行政法规", "D":"开展中央生态环境保护督察，坚决查处破坏生态环境的重大典型案件"}, "answer": "ABCD"}, # [cite: 8] # Option C had a "D" at the end, assuming it was part of the text and removed.
    {"id": "12_m7", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 7, "question": "7.共建清洁美丽世界，必须（  ）。", "options": {"A":"坚持以人为本", "B":"坚持多边主义", "C":"坚持共同但有区别的责任原则", "D":"坚持科学治理"}, "answer": "ABCD"}, # [cite: 8, 9]
    {"id": "12_m8", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 8, "question": "8.对我国推进碳达峰碳中和的理解，正确的说法是（   ）。", "options": {"A":"这是破解资源环境约束突出问题、实现可持续发展的迫切需要", "B":"这是一场广泛而深刻的经济社会系统性变革", "C":"实现“双碇”目标，是别人让我们这样做，不是我们自己要做", "D":"要把“双碇”工作纳入生态文明建设整体布局和经济社会发展全局", "E":"既坚定不移走绿色低碳发展的新路子，又不急于求成、偏激冒进"}, "answer": "ABDE"}, # [cite: 9]
    {"id": "12_m9", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 9, "question": "9.把建设美丽中国转化为全体人民自觉行动,要做到（  ）。", "options": {"A":"坚持用最严格制度最严密法治保护生态环境的同时，激发起全社会共同呵护生态环境的内生动力", "B":"增强全民节约意识、环保意识、生态意识", "C":"培育生态道德和行为准则，开展全民绿色行动", "D":"动员全社会都以实际行动减少能源资源消耗和污染排放", "E":"加快形成绿色生产方式和生活方式"}, "answer": "ABCDE"}, # [cite: 9]
    {"id": "12_m10", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 10, "question": "10.保护生态环境必须依靠制度、依靠法治,要做到（  ）。", "options": {"A":"构建产权清晰、多元参与、激励约束并重、系统完整的生态文明制度体系", "B":"实行最严格的生态环境保护制度", "C":"全面建立资源高效利用制度", "D":"严明生态环境保护责任制度", "E":"严格执行制度"}, "answer": "ABCDE"}, # [cite: 9]
    {"id": "12_m11", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 11, "question": "11.对共同但有区别的责任原则的理解，正确的说法是（  ）。", "options": {"A":"必须充分考虑历史责任、各国国情和生态治理能力", "B":"坚持各尽所能、国家自主决定贡献的制度安排", "C":"必须充分肯定发展中国家应对气候变化所作的贡献，照顾其特殊困难和关切", "D":"发达国家应该主动承担历史责任，为发展中国家提供资金、技术、能力建设等方面支持。", "E":"发达国家和发展中国家处于不同发展阶段，但在环境问题上的历史责任相同"}, "answer": "ABCD"}, # [cite: 9]
    {"id": "12_m12", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 12, "question": "12.推动全球可持续发展,我国必须（   ）。", "options": {"A":"积极参与全球气候治理", "B":"积极推进全球生物多样性治理", "C":"积极打造绿色“一带一路”", "D":"积极落实联合国生态系统恢复十年行动计划，实施生物多样性保护修复重大工程"}, "answer": "ABCD"}, # [cite: 9]
    {"id": "12_m13", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 13, "question": "13.在整个发展过程中，我们都要坚持（  ）的方针，要像保护眼睛一样保护生态环境", "options": {"A":"节约优先", "B":"发展为主", "C":"保护优先", "D":"自然恢复为主"}, "answer": "ACD"}, # [cite: 9]
    {"id": "12_m14", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 14, "question": "14.绿水青山就是金山银山，阐述了（  ）的关系。", "options": {"A":"社会和谐", "B":"经济发展", "C":"生态环境保护", "D":"人类生存"}, "answer": "BC"}, # [cite: 9]
    {"id": "12_m15", "type": "multiple", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 15, "question": "15.实现（   ）是我国向世界作出的庄严承诺，也是一场广泛而深刻的经济社会变革，绝不是轻轻松松就能实现的。", "options": {"A":"碳达峰", "B":"碳中和", "C":"建设美丽世界", "D":"构建人与自然的生命共同体"}, "answer": "AB"}, # [cite: 9]
    # Judgment (判断题) from 12.doc
    {"id": "12_j1", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 1, "question": "1.“天地与我并生，而万物与我为一”的“天人合一”思想是中华文明的鲜明特色和独特标识，代表着我们祖先对处理人与自然关系的重要认识。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 9]
    {"id": "12_j2", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 2, "question": "2.绿水青山可带来金山银山，金山银山也可买到绿水青山。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 9]
    {"id": "12_j3", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 3, "question": "3.生态环境保护和经济发展是矛盾对立的关系，是鱼和熊掌不可兼得的。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 9]
    {"id": "12_j4", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 4, "question": "4.建设生态文明是顺应人类文明进程.实现人与自然和谐共生的必然要求，具有历史必然性。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 9]
    {"id": "12_j5", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 5, "question": "5.良好生态环境是最普惠的民生福祉。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 9, 10]
    {"id": "12_j6", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 6, "question": "6.我们要优化国土空间开发保护格局，在自然保护地开发房地产。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 10]
    {"id": "12_j7", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 7, "question": "7.人和自然是生命共同体，人与自然是一种共生关系。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 10]
    {"id": "12_j8", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 8, "question": "8.要实现我国经济社会的可持续发展，必须着力开发利用传统能源，提高资源利用效率。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 10]
    {"id": "12_j9", "type": "judgment_as_single", "source_doc": "12.doc", "doc_order": 12, "q_num_in_doc": 9, "question": "9.发达国家应减少的是“奢侈排放”，中国则是最大限度地克制“生存和发展排放”。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 10]

    # --- Document 13.doc (doc_order: 13) ---
    # Single Choice (单项选择题)
    {"id": "13_s1", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 1, "question": "1.总体国家安全观以（  ）为宗旨，坚持国家安全一切为了人民。", "options": {"A":"人民安全", "B":"政治安全", "C":"国内安全", "D":"国际安全"}, "answer": "A"}, # [cite: 11]
    {"id": "13_s2", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 2, "question": "2.总体国家安全观以（   ）为基础，加强经济安全风险预警、防控机制和能力建设。", "options": {"A":"国土安全", "B":"经济安全", "C":"国内安全", "D":"国际安全"}, "answer": "B"}, # [cite: 11]
    {"id": "13_s3", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 3, "question": "3.(   )是应对国家安全形势新变化新趋势的战略选择，是全面贯彻落实总体国家安全观的重大举措。", "options": {"A":"统筹稳定和发展", "B":"构建新发展格局", "C":"构建新安全格局", "D":"建立强大的军队"}, "answer": "C"}, # [cite: 11]
    {"id": "13_s4", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 4, "question": "4.维护意识形态安全，最主要是（   ）。", "options": {"A":"落实意识形态工作责任制", "B":"把意识形态工作的领导权、管理权、话语权牢牢掌握在党的手中", "C":"及时掌握意识形态形势和动态", "D":"坚持和巩固马克思主义在意识形态领域的指导地位"}, "answer": "D"}, # [cite: 11]
    {"id": "13_s5", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 5, "question": "5. 维护政权安全，最主要是（   ）。", "options": {"A":"建立强大的军队", "B":"坚持和巩固马克思主义在意识形态领域的指导地位", "C":"坚持和巩固党的领导和长期执政地位", "D":"坚持和巩固人民民主专政"}, "answer": "C"}, # [cite: 11]
    {"id": "13_s6", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 6, "question": "6. 维护制度安全，最主要是（   ）。", "options": {"A":"坚持和完善中国特色社会主义制度", "B":"坚持和完善人民代表大会制度", "C":"推进国家治理体系和治理能力现代化", "D":"全面深化改革"}, "answer": "A"}, # [cite: 11, 12]
    {"id": "13_s7", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 7, "question": "7.（  ）是保障国家安全的治本之策。", "options": {"A":"增加经费投入", "B":"健全国家安全体系、加强国家安全制度建设", "C":"增强维护国家安全能力", "D":"建设更高水平的平安中国"}, "answer": "B"}, # [cite: 12]
    {"id": "13_s8", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 8, "question": "8.（  ）是人民幸福安康的基本要求，是安邦定国的重要基石。", "options": {"A":"国家富强", "B":"人民富裕", "C":"社会稳定", "D":"国家安全"}, "answer": "D"}, # [cite: 12]
    {"id": "13_s9", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 9, "question": "9.国家安全工作，归根结底是保障（  ），为群众安居乐业提供坚强保障。有了安全感，获得感才有保障，幸福感才会持久。", "options": {"A":"人民利益", "B":"社会稳定", "C":"经济发展", "D":"领土完整"}, "answer": "A"}, # [cite: 12]
    {"id": "13_s10", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 10, "question": "10.每年（  ）被确定为全民国家安全教育日。", "options": {"A":"4月15日", "B":"5月17日", "C":"6月15日", "D":"7月30日"}, "answer": "A"}, # [cite: 12]
    {"id": "13_s11", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 11, "question": "11.（   ）将“坚持总体国家安全观”纳入新时代坚持和发展中国特色社会主义的基本方略，并写入党章。", "options": {"A":"党的十八届三中全会", "B":"党的十九届六中全会", "C":"党的十九大", "D":"党的二十大"}, "answer": "C"}, # [cite: 12, 13]
    {"id": "13_s12", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 12, "question": "12.走中国特色国家安全道路，努力开创国家安全工作新局面，是对总体国家安全观的贯彻落实，归根到底是为了确保（   ）进程不被迟滞甚至中断。", "options": {"A":"社会主义现代化建设", "B":"全体人民共同富裕", "C":"中华民族伟大复兴", "D":"经济社会发展"}, "answer": "C"}, # [cite: 13]
    {"id": "13_s13", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 13, "question": "13.（  ）与人民群众切身利益关系最密切，是人民群众安全感的晴雨表，是社会安定的风向标。", "options": {"A":"政治安全", "B":"经济安全", "C":"社会安全", "D":"文化安全"}, "answer": "C"}, # [cite: 13]
    {"id": "13_s14", "type": "single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 14, "question": "14.面对波谲云诡的国际形势、复杂敏感的周边环境、艰巨繁重的改革发展稳定任务，我们必须树立（   ）。", "options": {"A":"忧患意识", "B":"零和思维", "C":"底线思维", "D":"全局意识"}, "answer": "C"}, # [cite: 13]
    # Multiple Choice (多项选择题) from 13.doc
    {"id": "13_m1", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 1, "question": "1.进入新时代，我国面临更为严峻复杂的国家安全形势，从外部环境来看，主要是（  ）。", "options": {"A":"世界战略格局、全球治理体系、综合国力竞争进入深度变迁的历史进程", "B":"气候变化、粮食安全、能源安全等全球性问题日趋尖锐复杂", "C":"地区热点和局部冲突此起彼伏，国际局势变得更加复杂动荡", "D":"和平与发展的时代主题面临严峻挑战"}, "answer": "ABCD"}, # [cite: 13]
    {"id": "13_m2", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 2, "question": "2.进入新时代，我国面临更为严峻复杂的国家安全形势，从内部环境来看，主要是（   ）。", "options": {"A":"重点领域关键环节改革任务仍然艰巨，科技创新能力存在卡点瓶颈", "B":"粮食、能源、资源、金融和产业链供应链安全面临重大考验", "C":"意识形态领域存在不少挑战，重点领域风险敞口加大", "D":"风险呈现形态更加复杂，既有显性风险又有隐性风险", "E":"既有可以预料的风险又有难以预料的风险，既有“黑天鹅”事件又有“灰犀牛”事件，而且各类风险成因多样、彼此交织"}, "answer": "ABCDE"}, # [cite: 13]
    {"id": "13_m3", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 3, "question": "3.当前我国所面临的新形势新挑战是（  ）。", "options": {"A":"正处于中华民族伟大复兴的关键时期", "B":"处于从发展中大国迈向社会主义现代化强国的关键阶段", "C":"中国式现代化越向前推进拓展", "D":"一些敌视中国共产党领导和我国社会主义制度的势力处心积虑地破坏，我们面临的压力和阻力越大"}, "answer": "ABCD"}, # [cite: 13]
    {"id": "13_m4", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 4, "question": "4.总体国家安全观强调（   ）。", "options": {"A":"做好国家安全工作的系统思维和方法，加强科学统筹", "B":"维护国家安全要贯穿党和国家工作各方面全过程", "C":"打总体战，形成汇聚党政军民学各战线各方面各层级的强大合力", "D":"全社会全政府全体系全手段应对重大国家安全风险挑战"}, "answer": "ABCD"}, # [cite: 13]
    {"id": "13_m5", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 5, "question": "5.总体国家安全观（  ）。", "options": {"A":"回答了如何解决好大国发展进程中面临的共性安全问题", "B":"回答了如何解决好中华民族伟大复兴关键时期面临的特殊安全问题", "C":"系统提出了一系列具有原创性、时代性的重要观点", "D":"为破解我国国家安全面临的难题、推进新时代国家安全工作提供了基本遵循"}, "answer": "ABCD"}, # [cite: 13]
    {"id": "13_m6", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 6, "question": "6.新时代国家安全得到全面加强,表现在（  ）。", "options": {"A":"党中央成立中央国家安全委员会", "B":"制定实施《中国共产党领导国家安全工作条例》", "C":"制定出台国家情报法、反恐怖主义法等一系列国家安全法律法规", "D":"制定实施《国家安全战略纲要》《国家安全战略（2021-2025年）》", "E":"国家安全体系和能力建设取得突破性进展"}, "answer": "ABCDE"}, # [cite: 13]
    {"id": "13_m7", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 7, "question": "7.对发展和安全的理解，正确的观点是（  ）。", "options": {"A":"发展解决的是动力问题，是推动国家和民族康续绵延的根本支撑", "B":"安全解决的是保障问题，是确保国家和民族行稳致远的坚强柱石", "C":"发展具有基础性、根本性，是解决安全问题的总钥匙", "D":"没有国家安全,发展取得的成果也可能毁于一旦", "E":"发展和安全是一体之两翼、驱动之双轮，必须同步推进"}, "answer": "ABCDE"}, # [cite: 13]
    {"id": "13_m8", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 8, "question": "8.对新安全格局和新发展格局关系的正确理解是（   ）。", "options": {"A":"新安全格局是新发展格局的重要前提和保障。", "B":"只有以新安全格局保障新发展格局，才能夯实我国经济发展的根基、增强发展的安全性稳定性", "C":"只有以新安全格局保障新发展格局，才能在各种可以预见和难以预见的风险挑战中增强我国的生存力、竞争力、发展力、持续力", "D":"以新安全格局保障新发展格局，必须统筹维护国家安全各类要素、各方资源、各种手段，主动塑造有利的外部安全环境"}, "answer": "ABCD"}, # [cite: 13]
    {"id": "13_m9", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 9, "question": "9.政治安全涉及国家（   ）的稳固，是一个国家最根本的需求。", "options": {"A":"主权", "B":"政权", "C":"制度", "D":"意识形态"}, "answer": "ABCD"}, # [cite: 13, 14]
    {"id": "13_m10", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 10, "question": "10. 维护政治安全，要（    ）。", "options": {"A":"维护政权安全", "B":"维护制度安全", "C":"维护意识形态安全", "D":"维护中国共产党执政安全"}, "answer": "ABCD"}, # [cite: 14]
    {"id": "13_m11", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 11, "question": "11. 政治安全与人民安全、国家利益至上的关系是（   ）。", "options": {"A":"要把政治安全、人民安全、国家利益至上三者统一起来，确保实现党的长期执政、人民安居乐业、国家长治久安", "B":"政治安全是维护人民安全和国家利益的根本保证", "C":"人民安全居于中心地位，国家安全归根到底是保障人民利益", "D":"国家利益至上是实现政治安全和人民安全的要求和原则。"}, "answer": "ABCD"}, # [cite: 14]
    {"id": "13_m12", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 12, "question": "12.国土安全是立国之基，维护国土安全，要（  ）。", "options": {"A":"提升维护国土安全能力，加强边防、海防、空防建设", "B":"坚决反对一切分裂祖国的活动", "C":"深入打击恐怖主义、分裂主义、极端主义“三股势力”", "D":"坚决防范“藏独”“东突”，坚决粉碎任何“台独”分裂图谋", "E":"全力维护香港、澳门长期繁荣稳定"}, "answer": "ABCDE"}, # [cite: 14]
    {"id": "13_m13", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 13, "question": "13.经济安全是国家安全的基础, 维护经济安全,要（ ）。", "options": {"A":"保证基本经济制度安全，维护社会主义市场经济秩序", "B":"加快建设现代化经济体系，提升产业链供应链韧性和安全水平。", "C":"加强金融、地方债务风险防控，守住不发生系统性风险的底线。", "D":"保障经济社会发展所需的资源能源持续、可靠和有效供给。", "E":"全方位夯实粮食安全根基，牢牢守住18亿亩耕地红线"}, "answer": "ABCDE"}, # [cite: 14]
    {"id": "13_m14", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 14, "question": "14. 健全国家安全体系，要（   ）。", "options": {"A":"坚持党中央对国家安全工作的集中统一领导，完善高效权威的国家安全领导体制", "B":"强化国家安全工作协调机制", "C":"完善国家安全法治体系、战略体系、政策体系、风险监测预警体系、国家应急管理体系", "D":"完善重点领域安全保障体系和重要专项协调指挥体系", "E":"加快涉外法治工作战略布局，健全反制裁、反干涉、反“长臂管辖”机制。"}, "answer": "ABCDE"}, # [cite: 14]
    {"id": "13_m15", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 15, "question": "15. 建设平安中国，必须（    ）。", "options": {"A":"聚焦影响国家安全和社会稳定的突出问题", "B":"坚持安全第一、预防为主，建立大安全大应急框架", "C":"推动公共安全治理模式由以事后处置为主向以事前预防为主转型", "D":"推进安全生产风险专项整治，加强重点行业、重点领域安全监管。", "E":"加强国家区域应急力量建设"}, "answer": "ABCDE"}, # [cite: 14]
    {"id": "13_m16", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 16, "question": "16.提高防范化解重大风险能力,要（  ）。", "options": {"A":"坚持底线思维和极限思维,从最坏处着眼，做最充分的准备", "B":"既要有防范风险的先手，也要有应对和化解风险挑战的高招", "C":"既要打好防范和抵御风险的有准备之战，也要打好化险为夷、转危为机的战略主动战", "D":"既要高度警惕“黑天鹅”事件，也要防范“灰犀牛”事件", "E":"在重大风险、强大对手面前，总想过太平日子、不想斗争是不切实际的"}, "answer": "ABCDE"}, # [cite: 14]
    {"id": "13_m17", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 17, "question": "17. 总体国家安全观以（  ）为保障，建立完善强基固本、化险为夷的各项对策措施，为维护国家安全提供硬实力和软实力保障。", "options": {"A":"军事安全", "B":"科技安全", "C":"文化安全", "D":"社会安全"}, "answer": "ABCD"}, # [cite: 14]
    # Judgment (判断题) from 13.doc
    {"id": "13_j1", "type": "judgment_as_single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 1, "question": "1.发展和安全是一体之两翼、驱动之双轮。发展是安全的基础和目的，安全是发展的条件和保障，发展和安全要同步推进。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 14, 15]
    {"id": "13_j2", "type": "judgment_as_single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 2, "question": "2.政治安全是立国之基。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 15]
    {"id": "13_j3", "type": "judgment_as_single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 3, "question": "3. 推进国家安全体系和能力现代化，是新时代维护国家安全的迫切要求，也是推进国家治理体系和治理能力现代化的重要工程。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 15]
    {"id": "13_j4", "type": "judgment_as_single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 4, "question": "4. 生物安全问题已经成为全世界、全人类面临的重大生存和发展威胁之一，重大传染病和生物安全风险是事关国家安全和发展、事关社会大局稳定的重大风险挑战。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 15]
    {"id": "13_j5", "type": "judgment_as_single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 5, "question": "5.没有网络安全就没有国家安全，就没有经济社会稳定运行，广大人民群众利益也难以得到保障。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 15]
    {"id": "13_j6", "type": "judgment_as_single", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 6, "question": "6. 经济安全与人民群众切身利益关系最密切，是人民群众安全感的晴雨表，是社会安定的风向标", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 15]

    # --- Document 14.doc (doc_order: 14) ---
    # Single Choice (单项选择题)
    {"id": "14_s1", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 1, "question": "1.党的十八大以来，以习近平同志为核心的党中央围绕新时代（ ），深入进行理论探索和实践创造，形成习近平强军思想。", "options": {"A":"坚持和发展什么样的中国特色社会主义、怎样坚持和发展中国特色社会主义", "B":"建设什么样的社会主义现代化强国、怎样建设社会主义现代化强国", "C":"建设什么样的长期执政的马克思主义政党、怎样建设长期执政的马克思主义政党", "D":"建设一支什么样的强大人民军队、怎样建设强大人民军队"}, "answer": "D"}, # [cite: 17]
    {"id": "14_s2", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 2, "question": "2.习近平强军思想明确(  )是人民军队建军之本、强军之魂.", "options": {"A":"政治工作", "B":"党对人民军队的绝对领导", "C":"练兵备战", "D":"先进科技"}, "answer": "B"}, # [cite: 17]
    {"id": "14_s3", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 3, "question": "3.把（ ）作为唯一的根本的标准，是有效履行我军根本职能的内在要求，也是提高军队建设质量效益的客观需要。", "options": {"A":"政治建军", "B":"军事改革", "C":"战斗力", "D":"军事创新"}, "answer": "C"}, # [cite: 17]
    {"id": "14_s4", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 4, "question": "4.(  )明确提出，党在新时代的强军目标是建设一支听党指挥、能打胜仗、作风优良的人民军队,把人民军队建设成为世界一流军队。", "options": {"A":"2012年12月，中央军委扩大会议", "B":"党的十九大", "C":"2013年3月，十二届全国人大一次会议", "D":"党的二十大"}, "answer": "B"}, # [cite: 17]
    {"id": "14_s5", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 5, "question": "5. 在新时代的强军目标中，（  ）是核心。", "options": {"A":"听党指挥", "B":"能打胜仗", "C":"作风优良", "D":"全面建成世界一流军队"}, "answer": "B"}, # [cite: 17]
    {"id": "14_s6", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 6, "question": "6. 90多年来，人民军队之所以能够始终保持强大的凝聚力向心力战斗力，经受住各种考验，不断从胜利走向胜利，最根本的就是靠（   ）。", "options": {"A":"一不怕苦，二不怕死", "B":"中国共产党的坚强领导", "C":"改革开放的成功", "D":"发展先进科学技术"}, "answer": "B"}, # [cite: 17]
    {"id": "14_s7", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 7, "question": "7.（ ）是人民军队的鲜明特色和政治优势，也是人民军队战无不胜、攻无不克的重要保证。", "options": {"A":"能打胜仗", "B":"军民情谊", "C":"听党指挥", "D":"作风优良"}, "answer": "D"}, # [cite: 17, 18]
    {"id": "14_s8", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 8, "question": "8. 要充分发挥政治工作对强军兴军的生命线作用，培养有灵魂、（ ）、有血性、有品德的新时代革命军人。", "options": {"A":"不怕苦", "B":"有本事", "C":"淡泊名利", "D":"崇尚光荣"}, "answer": "B"}, # [cite: 18]
    # Note: 14.doc has two questions numbered 8 and 9, then another 8, 9, 10 in single choice. I'll number them sequentially for q_num_in_doc.
    {"id": "14_s9", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 9, "question": "9. 力争到二〇三五年（ ）国防和军队现代化，到本世纪中叶把人民军队（ ）世界一流军队。", "options": {"A":"全面实现；基本建成", "B":"全面实现；全面建成", "C":"基本实现；基本建成", "D":"基本实现；全面建成"}, "answer": "D"}, # [cite: 18]
    {"id": "14_s10", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 10, "question": "10. 军队是要准备打仗的，一切工作都必须坚持（  ）标准，向能打仗、打胜仗聚焦。", "options": {"A":"战斗力", "B":"斗争力", "C":"战争力", "D":"硬实力"}, "answer": "A"}, # [cite: 18, 19]
    {"id": "14_s11", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 11, "question": "8.（  ）是党指挥枪原则落地生根的坚实基础。", "options": {"A":"支部建在排上", "B":"支部建在连上", "C":"支部建在营上", "D":"支部建在团上"}, "answer": "B"}, # [cite: 19] # Original number 8
    {"id": "14_s12", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 12, "question": "9. 国防和军队改革取得历史性突破，形成军委管总、战区主战、（ ）新格局，人民军队组织架构和力量体系实现革命性重塑。", "options": {"A":"党委领导", "B":"战区主建", "C":"军种主战", "D":"军种主建"}, "answer": "D"}, # [cite: 19] # Original number 9
    {"id": "14_s13", "type": "single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 13, "question": "10.（ ）,是决定军队建设的政治方向。", "options": {"A":"军民融合是关键", "B":"能打胜仗是核心", "C":"听党指挥是灵魂", "D":"作风优良是保证"}, "answer": "C"}, # [cite: 19] # Original number 10
    # Multiple Choice (多项选择题) from 14.doc
    {"id": "14_m1", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 1, "question": "1. 推进强军事业必须坚持（   ）。", "options": {"A":"政治建军", "B":"改革强军", "C":"科技强军", "D":"人才强军", "E":"依法治军"}, "answer": "ABCDE"}, # [cite: 19]
    {"id": "14_m2", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 2, "question": "2. 新时代人民军队使命任务是（   ）。", "options": {"A":"为巩固中国共产党领导和我国社会主义制度提供战略支撑", "B":"为捍卫国家主权、统一和领土完整提供战略支撑", "C":"为维护我国海外利益提供战略支撑", "D":"为促进世界和平与发展提供战略支撑"}, "answer": "ABCD"}, # [cite: 19]
    {"id": "14_m3", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 3, "question": "3.进入新时代，我国军队建设存在的问题是（ ）。", "options": {"A":"军队现代化水平与国家安全需求相比差距还很大", "B":"军队现代化水平与世界先进军事水平相比差距还很大", "C":"军队打现代化战争能力不够", "D":"各级干部指挥现代化战争能力不够"}, "answer": "ABCD"}, # [cite: 19]
    {"id": "14_m4", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 4, "question": "4.党在新时代强军目标的科学内涵是（ ）。", "options": {"A":"听党指挥是灵魂，决定军队建设的政治方向", "B":"能打胜仗是核心，反映军队的根本职能和军队建设的根本指向", "C":"作风优良是保证，关系军队的性质、宗旨、本色", "D":"体现了坚持党的建军原则、人民军队根本职能、特有政治优势的高度统一"}, "answer": "ABCD"}, # [cite: 19]
    {"id": "14_m5", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 5, "question": "5.党在新时代的强军目标是建设一支（   ）的人民军队。", "options": {"A":"听党指挥", "B":"能打胜仗", "C":"作风优良", "D":"敢于创新"}, "answer": "ABC"}, # [cite: 19, 20]
    {"id": "14_m6", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 6, "question": "6.我国国防和军队建设“新三步走” 战略安排是（  ）。", "options": {"A":"到2027年，实现建军一百年奋斗目标", "B":"到2035年，基本实现国防和军队现代化", "C":"到本世纪中叶，把人民军队全面建成世界一流军队", "D":"到2050年，全面实现军事作战无人化、智能化"}, "answer": "ABC"}, # [cite: 20]
    {"id": "14_m7", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 7, "question": "7.到2035年，基本实现国防和军队现代化，这一步的关键是实现（  ）。", "options": {"A":"军事理论现代化", "B":"军队组织形态现代化", "C":"军事人员现代化", "D":"武器装备现代化"}, "answer": "ABCD"}, # [cite: 20]
    {"id": "14_m8", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 8, "question": "8. 到本世纪中叶,把人民军队全面建成世界一流军队,具体的目标要求是（）。", "options": {"A":"建成同我国强国地位相称的世界一流军队", "B":"建成能够全面有效维护国家安全的世界一流军队", "C":"建成具备强大国际影响力的世界一流军队", "D":"能够打败一切强敌的世界一流军队"}, "answer": "ABC"}, # [cite: 20]
    {"id": "14_m9", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 9, "question": "9. 坚持党对人民军队的绝对领导必须有一整套制度作保证。这些制度主要有（ ）。", "options": {"A":"军队最高领导权和指挥权属于党中央、中央军委，中央军委实行主席负责制", "B":"实行党委制、政治委员制、政治机关制", "C":"实行党委（支部）统一的集体领导下的首长分工负责制", "D":"实行支部建在连上"}, "answer": "ABCD"}, # [cite: 20]
    {"id": "14_m10", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 10, "question": "10.新的征程上，开创国防和军队现代化新局面，必须全面推进（ ）, 加快把人民军队建设成为世界一流军队。", "options": {"A":"政治建军", "B":"改革强军", "C":"科技强军", "D":"人才强军", "E":"依法治军"}, "answer": "ABCDE"}, # [cite: 20]
    {"id": "14_m11", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 11, "question": "11.要着力培养新时代革命军人，锻造具有（  ）的过硬部队，确保我军永远立于不败之地。", "options": {"A":"铁一般信仰", "B":"铁一般信念", "C":"铁一般纪律", "D":"铁一般担当"}, "answer": "ABCD"}, # [cite: 20, 21]
    {"id": "14_m12", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 12, "question": "12. 深化国防和军队改革，要（    ）。", "options": {"A":"按照军委管总、战区主战、军种主建的总原则改革领导指挥体制", "B":"推进军队规模结构和力量编成改革，构建中国特色现代军事力量体系", "C":"深化军队党的建设制度改革、创新军事力量运用政策制度", "D":"重塑军事力量建设政策制度、改革军事管理政策制度", "E":"建立健全中国特色社会主义军事政策制度体系"}, "answer": "ABCDE"}, # [cite: 21]
    {"id": "14_m13", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 13, "question": "13.贯彻依法治军战略，要紧紧围绕党在新时代的强军目标,着眼全面加强革命化现代化正规化建设，坚持（    ）。", "options": {"A":"党对人民军队的绝对领导", "B":"建设中国特色军事法治体系", "C":"从严治军铁律", "D":"抓住领导干部这个“关键少数”", "E":"按照法治要求转变治军方式"}, "answer": "ABCDE"}, # [cite: 21]
    {"id": "14_m14", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 14, "question": "14. 提高军队战斗力，要（    ）。", "options": {"A":"强化战斗队思想，立起练兵备战鲜明导向", "B":"做到全部精力向打仗聚焦", "C":"坚决破除“和平积弊”，把战斗力标准贯彻到全军各项建设中", "D":"坚持用是否有利于提高战斗力来衡量和检验各项工作"}, "answer": "ABCD"}, # [cite: 21]
    {"id": "14_m15", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 15, "question": "15. 对“强国必须强军，军强才能国安”的正确理解是（ ）。", "options": {"A":"国无防不立，民无兵不安。没有一支强大的军队，就不可能有强大的祖国", "B":"中国越发展壮大，遇到的阻力和压力就会越大，面临的风险就会越多", "C":"面对严峻复杂的国家安全形势，必须对战争危险保持清醒头脑。", "D":"能战方能止战，要实现中华民族伟大复兴，就必须把军队搞得更强大"}, "answer": "ABCD"}, # [cite: 21]
    {"id": "14_m16", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 16, "question": "16. 之所以必须坚持党对人民军队的绝对领导，是因为（ ）。", "options": {"A":"坚持党对人民军队的绝对领导，是马克思主义建党建军的一条基本原则", "B":"党对人民军队的绝对领导，是建军之本、强军之魂", "C":"人民军队是党缔造的，始终在党的领导下行动和战斗", "D":"党的绝对领导，造就了人民军队对党的赤胆忠心、为党和人民冲锋陷阵的坚定意志", "E":"坚定不移听党话、跟党走，是人民军队永葆人民军队性质、本色的根本保证"}, "answer": "ABCDE"}, # [cite: 21]
    {"id": "14_m17", "type": "multiple", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 17, "question": "17.武器装备远程（  ）趋势更加明显，战争形态加速向信息化战争演变，智能化战争初现端倪。。", "options": {"A":"精确化", "B":"智能化", "C":"隐身化", "D":"无人化"}, "answer": "ABCD"}, # [cite: 21]
    # Judgment (判断题) from 14.doc
    {"id": "14_j1", "type": "judgment_as_single", "source_doc": "14.doc", "doc_order": 14, "q_num_in_doc": 1, "question": "1.坚持党对人民军队的绝对领导是人民军队能打仗、打胜仗的军事战略指导。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 21]
    {"id": "14_j2", "type": "judgment_as_single", "source_doc": "14.doc", "doc_order":  14, "q_num_in_doc": 2, "question": "2. 军事战略科学准确，就是最大的胜算。要增强军事战略指导的进取性和主动性，把备战与止战、威慑与实战、战争行动与和平时期军事力量运用作为一个整体加以运筹。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 21]

    # --- Document 15.doc (doc_order: 15) ---
    # Single Choice (单项选择题)
    {"id": "15_s1", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 1, "question": "1.“一国两制”伟大构想，最早是针对(  )提出来的。", "options": {"A":"香港问题", "B":"澳门问题", "C":"金门问题", "D":"台湾问题"}, "answer": "D"}, # [cite: 23]
    {"id": "15_s2", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 2, "question": "2.“一国两制”的根本宗旨是(   )。", "options": {"A":"保持香港、澳门长期繁荣稳定", "B":"解决台湾问题", "C":"维护国家主权、安全、发展利益，保持香港、澳门长期繁荣稳定", "D":"实现中华民族伟大复兴"}, "answer": "C"}, # [cite: 23]
    {"id": "15_s3", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 3, "question": "3.(   )，这是实现祖国统一的战略思路。", "options": {"A":"坚持“和平统一、一国两制”基本方针", "B":"坚持一个中国原则和“九二共识”", "C":"坚持推动两岸关系融合发展", "D":"坚持在祖国大陆发展进步基础上解决台湾问题"}, "answer": "D"}, # [cite: 23]
    {"id": "15_s4", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 4, "question": "4.（   ）是两岸关系的政治基础。", "options": {"A":"继续推进两岸“三通”", "B":"促进两岸人文交流", "C":"协商解决两岸同胞关心的问题", "D":"一个中国原则"}, "answer": "D"}, # [cite: 23]
    {"id": "15_s5", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 5, "question": "5.“一国两制”是一个完整的概念。“一国”是实行“两制”的（ ），“两制”从属和派生于“一国”并统一于“一国”之内。", "options": {"A":"目标和原则", "B":"前提和基础", "C":"方向和路径", "D":"结果和目标"}, "answer": "B"}, # [cite: 23]
    {"id": "15_s6", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 6, "question": "6.中央政府对特别行政区拥有（  ），这是特别行政区高度自治权的源头。", "options": {"A":"自主选择权", "B":"全面管治权", "C":"高度管理权", "D":"立法管治权"}, "answer": "B"}, # [cite: 23, 24]
    {"id": "15_s7", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 7, "question": "7.能够确保香港、澳门回归后长期繁荣稳定的最佳制度是（    ）。", "options": {"A":"一国两制", "B":"社会主义制度", "C":"资本主义制度", "D":"中西结合制度"}, "answer": "A"}, # [cite: 24]
    {"id": "15_s8", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 8, "question": "8.两岸关系和平发展的最大障碍是（    ）。", "options": {"A":"“台独”", "B":"制度不同", "C":"经济发展水平不同", "D":"信仰不同"}, "answer": "A"}, # [cite: 24]
    {"id": "15_s9", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 9, "question": "9.(   )，这是实现祖国统一的战略支撑。", "options": {"A":"坚持党中央对对台工作的集中统一领导", "B":"坚持反对外部势力干涉", "C":"坚持团结台湾同胞、争取台湾民心", "D":"坚持粉碎“台独”分裂图谋", "E":"坚持决不承诺放弃使用武力"}, "answer": "E"}, # [cite: 24]
    {"id": "15_s10", "type": "single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 10, "question": "10.澳门、香港特别行政区现任行政长官分别是（  ）", "options": {"A":"林郑月娥 崔世安", "B":"李家超 贺一诚", "C":"何厚铧林 林郑月娥", "D":"梁振英 李家超", "E":"贺一诚 李家超"}, "answer": "E"}, # [cite: 24]
    # Multiple Choice (多项选择题) from 15.doc
    {"id": "15_m1", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 1, "question": "1.在“一国两制”之下，作为直辖于中央人民政府的香港、澳门特别行政区，享有高度自治权，包括（   ）。", "options": {"A":"行政管理权", "B":"立法权", "C":"独立的司法权和终审权", "D":"外交权"}, "answer": "ABC"}, # [cite: 24]
    {"id": "15_m2", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 2, "question": "2.“一国两制”（  ）。", "options": {"A":"是中国特色社会主义的伟大创举", "B":"是中国特色社会主义制度创新的重要成果", "C":"是中国共产党领导人民实现祖国和平统一的伟大构想", "D":"为国际社会解决类似问题提供了新思路新方案", "E":"包含了中华文化中的和合理念，体现了尊重差异、求同存异的思维方式"}, "answer": "ABCDE"}, # [cite: 24]
    {"id": "15_m3", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 3, "question": "3.对中央全面管治权和特别行政区高度自治权的正确理解是（ ）。", "options": {"A":"中央对包括香港、澳门特别行政区在内的所有地方行政区域拥有全面管治权。", "B":"全面管治权是授权特别行政区高度自治的前提和基础，高度自治权是中央行使全面管治权的体现", "C":"它们之间是源与流、本与末的关系", "D":"高度自治不是完全自治,而是中央授予的地方事务管理权", "E":"中央有权对特别行政区高度自治权行使情况进行监督"}, "answer": "ABCDE"}, # [cite: 24]
    {"id": "15_m4", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 4, "question": "4.坚持和完善“一国两制”制度体系,要（   ）。", "options": {"A":"加强依法治理相关制度和机制建设", "B":"健全中央行使全面管治权的制度", "C":"为落实爱国者治理提供制度保障", "D":"要继续发展壮大爱国爱港爱澳力量，增强港澳同胞的爱国精神"}, "answer": "ABCD"}, # [cite: 24, 25]
    {"id": "15_m5", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 5, "question": "5.落实“爱国者治港”“爱国者治澳”原则,（  ）。", "options": {"A":"事关特别行政区的管治权掌握在谁手中", "B":"事关国家主权、安全、发展利益", "C":"事关香港、澳门长期繁荣稳定", "D":"是保证香港、澳门长治久安的必然要求"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m6", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 6, "question": "6.爱国者的标准是客观的、清晰的，就是（ ）。", "options": {"A":"尊重自己民族，诚心诚意拥护祖国恢复行使对香港、澳门的主权，不损害香港、澳门的繁荣和稳定", "B":"在香港、澳门回归祖国之后，就是要求爱国者必须真心维护国家主权、安全、发展利益", "C":"尊重和维护宪法和基本法确定的宪制秩序", "D":"维护香港、澳门的繁荣稳定"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m7", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 7, "question": "7.为了解决香港特别行政区在维护国家安全领域长期“不设防”的状况，中央人民政府采取的措施有（  ）。", "options": {"A":"2020年5月，十三届全国人大三次会议通过《全国人民代表大会关于建立健全香港特别行政区维护国家安全的法律制度和执行机制的决定》。", "B":"2020年6月，十三届全国人大常委会第二十次会议通过《中华人民共和国香港特别行政区维护国家安全法》", "C":"中央人民政府依法设立驻香港特别行政区维护国家安全公署", "D":"2022年12月，十三届全国人大常委会第三十八次会议通过《关于〈中华人民共和国香港特别行政区维护国家安全法〉第十四条和第四十七条的解释》"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m8", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 8, "question": "8.为了全面贯彻并落实“爱国者治港”原则，党中央采取措施，完善香港特别行政区选举制度，具体表现在（   ）。", "options": {"A":"2021年3月，十三届全国人大四次会议通过《全国人民代表大会关于完善香港特别行政区选举制度的决定》", "B":"2021年,十三届人大常委会第二十七次会议通过新修订的《中华人民共和国香港特别行政区基本法附件一香港特别行政区行政长官的产生办法》《中华人民共和国香港特别行政区基本法附件二香港特别行政区立法会的产生办法和表决程序》。", "C":"2021年5月，香港特别行政区立法会通过《2021年完善选举制度（综合修订）条例草案》", "D":"2022年12月，十三届全国人大常委会第三十八次会议通过《关于〈中华人民共和国香港特别行政区维护国家安全法〉第十四条和第四十七条的解释》"}, "answer": "ABC"}, # [cite: 25]
    {"id": "15_m9", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 9, "question": "9.面对香港局势动荡变化，党中央审时度势，采取哪些标本兼治的举措, 推动香港局势实现由乱到治的重大转折。（  ）", "options": {"A":"建立健全香港特别行政区维护国家安全的法律制度和执行机制", "B":"完善香港特别行政区选举制度", "C":"坚持以行政长官为核心的行政主导体制", "D":"支持行政长官和特别行政区政府依法施政、积极作为"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m10", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 10, "question": "10.在新时代国家改革开放进程中,香港、澳门应该如何抓住发展机遇，更好融入国家发展大局。（ ）", "options": {"A":"积极主动助力国家全面开放", "B":"积极主动参与粤港澳大湾区建设", "C":"积极主动参与国家治理实践", "D":"积极主动促进国际人文交流"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m11", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 11, "question": "11.解决台湾问题、实现祖国完全统一，是（  ）。", "options": {"A":"党矢志不渝的历史任务", "B":"全体中华儿女的共同愿望", "C":"实现中华民族伟大复兴的必然要求", "D":"大势所趋、大义所在、民心所向"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m12", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 12, "question": "12.（  ）是我们解决台湾问题的最大底气。", "options": {"A":"中国特色社会主义事业取得的伟大成就", "B":"我国经济、科技、国防实力的持续增强", "C":"包括台湾人民在内的全国各族人民万众一心、同仇敌忾", "D":"国际社会支持"}, "answer": "ABC"}, # [cite: 25]
    {"id": "15_m13", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 13, "question": "13.牢牢把握两岸关系主导权和主动权，要做到（  ）。", "options": {"A":"坚持“和平统一、一国两制”方针，探索“两制”台湾方案", "B":"坚定支持岛内爱国统一力量，坚定反“独”促统", "C":"促进两岸经济文化交流合作，深化两岸各领域融合发展", "D":"坚持以最大诚意、尽最大努力争取和平统一的前景，但决不承诺放弃使用武力"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m14", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 14, "question": "14.全面贯彻新时代党解决台湾问题的总体方略，必须(   )。", "options": {"A":"坚持党中央对对台工作的集中统一领导", "B":"坚持在中华民族伟大复兴进程中推进祖国统一", "C":"坚持在祖国大陆发展进步基础上解决台湾问题", "D":"坚持“和平统一、一国两制”基本方针", "E":"坚持一个中国原则和“九二共识”"}, "answer": "ABCDE"}, # [cite: 25]
    {"id": "15_m15", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 15, "question": "15.祖国完全统一一定要实现，也一定能够实现，因为（  ）。", "options": {"A":"实现祖国完全统一是中华民族伟大复兴的必然要求,是不可阻挡的历史潮流", "B":"台湾前途在于国家统一，台湾同胞福祉系于民族复兴", "C":"国家统一是大势所趋、大义所在、民心所向,台湾问题因民族弱乱而产生，必将随着民族复兴而解决", "D":"“台独”是历史逆流，是绝路,我们绝不为各种形式的“台独”分裂活动留下任何空间"}, "answer": "ABCD"}, # [cite: 25]
    {"id": "15_m16", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 16, "question": "16.党的十八大以来，党中央全面准确贯彻“一国两制”方针，牢牢掌握（   ）赋予的中央对香港、澳门全面管治权。", "options": {"A":"宪法", "B":"基本法", "C":"民法", "D":"刑法"}, "answer": "AB"}, # [cite: 25, 26]
    {"id": "15_m17", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 17, "question": "17. 以下关于“一国”和“两制”的关系，正确的是（    ）。", "options": {"A":"“一国两制”是一个完整的概念", "B":"“一国”是实行“两制”的前提和基础", "C":"“两制”从属和派生于“一国”，并统一于“一国”之内", "D":"“一国”之内的“两制”并非等量齐观，国家的主体必须实行社会主义制度，特别行政区所有居民应该自觉尊重和维护国家的根本制度。"}, "answer": "ABCD"}, # [cite: 26] # Renamed option D key from " " to "D"
    {"id": "15_m18", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 18, "question": "18.全面准确贯彻“一国两制”方针，必须（    ）。", "options": {"A":"始终准确把握“一国”和“两制”的关系", "B":"落实中央对特别行政区全面管治权，维护国家主权、安全、发展利益", "C":"聚焦发展这个第一要务，推动港澳融入国家发展大局", "D":"坚持爱国者治港治澳原则"}, "answer": "ABCD"}, # [cite: 26]
    # Judgment (判断题) from 15.doc
    {"id": "15_j1", "type": "judgment_as_single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 1, "question": "1.对香港、澳门来说，“一国两制”是最大的优势，国家改革开放是最大的舞台，共建“一带一路”、粤港澳大湾区建设等国家战略实施是新的重大机遇。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 26]
    {"id": "15_j2", "type": "judgment_as_single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 2, "question": "2.两岸关系的政治基础是“一个中国”原则。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 26]
    {"id": "15_j3", "type": "judgment_as_single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 3, "question": "3.香港是我国内地最大的外资来源地、对外投资最大目的地、对外贸易最大转口地，澳门是我国双向开放特别是与葡语国家经贸往来的重要平台。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 26]
    {"id": "15_j4", "type": "judgment_as_single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 4, "question": "4.必须始终维护中央全面管治权，在任何时候，都不能将全面管治权和高度自治权对立起来；在任何情况下，特别行政区行使高度自治权都不得损害国家主权和全面管治权，更不能以高度自治权对抗全面管治权。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 26]
    {"id": "15_j5", "type": "judgment_as_single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 5, "question": "5.台湾问题因民族弱乱而产生，必将随着民族复兴而解决.台湾前途在于国家统一，台湾同胞福祉系于民族复兴。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 26]
    {"id": "15_j6", "type": "judgment_as_single", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 6, "question": "6.党的十八大以来，党中央全面准确贯彻“一国两制”方针，牢牢掌握（   ）赋予的中央对香港、澳门全面管治权。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 26]

    # --- Document 16.doc (doc_order: 16) ---
    # Single Choice (单项选择题)
    {"id": "16_s1", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 1, "question": "1.坚持以（  ）为统领加强党对对外工作的集中统一领导。", "options": {"A":"实现中华民族伟大复兴", "B":"维护党中央权威", "C":"政治纪律", "D":"党中央"}, "answer": "B"}, # [cite: 28]
    {"id": "16_s2", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 2, "question": "2.坚持以（  ）为原则推动“一带一路”建设。", "options": {"A":"平等协商", "B":"互利共赢", "C":"共商共建", "D":"共商共建共享"}, "answer": "D"}, # [cite: 28]
    {"id": "16_s3", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 3, "question": "3.坚持以（  ）为底线维护国家主权、安全、发展利益", "options": {"A":"和平发展", "B":"国土完整", "C":"互惠互利", "D":"国家核心利益"}, "answer": "D"}, # [cite: 28]
    {"id": "16_s4", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 4, "question": "4.坚持以（   ）为理念引领全球治理体系改革。", "options": {"A":"公平正义", "B":"集体安全", "C":"绿色发展", "D":"高质量发展"}, "answer": "A"}, # [cite: 28]
    {"id": "16_s5", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 5, "question": "5.坚持以(  )为宗旨推动构建人类命运共同体。", "options": {"A":"中华民族伟大复兴", "B":"维护世界和平、促进共同发展", "C":"以共商共建共享", "D":"维护党中央权威"}, "answer": "B"}, # [cite: 28]
    {"id": "16_s6", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 6, "question": "6.（  ）是新时代中国外交的基本原则。", "options": {"A":"互相尊重", "B":"坚持走和平发展道路", "C":"礼尚往来", "D":"开放包容"}, "answer": "B"}, # [cite: 28]
    {"id": "16_s7", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 7, "question": "7.构建人类命运共同体思想，核心是“建设持久和平、普遍安全、共同繁荣、(  )的世界”。", "options": {"A":"合作共赢、持续发展", "B":"开放包容、合作共赢", "C":"合作共赢、清洁美丽", "D":"开放包容、清洁美丽"}, "answer": "D"}, # [cite: 28, 29]
    {"id": "16_s8", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 8, "question": "8.（ ）是构建人类命运共同体的重要思想基础，凝聚了人类不同文明的价值共识。", "options": {"A":"人类理想追求", "B":"全人类共同价值", "C":"全球经济发展", "D":"世界一体化建设"}, "answer": "B"}, # [cite: 29]
    {"id": "16_s9", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 9, "question": "9.新型国际关系“新”在（    ）。", "options": {"A":"经济发展", "B":"合作共赢", "C":"开放包容", "D":"人类文明"}, "answer": "B"}, # [cite: 29]
    {"id": "16_s10", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 10, "question": "10.坚持以（   ）为依托打造全球伙伴关系。", "options": {"A":"深化外交布局", "B":"维护世界和平、促进共同发展", "C":"共商共建共享", "D":"维护党中央权威"}, "answer": "A"}, # [cite: 29]
    {"id": "16_s11", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 11, "question": "11.（  ）是我国对外工作的出发点和落脚点,是中国外交的神圣使命。。", "options": {"A":"维护我国人民的利益", "B":"维护世界人民的利益", "C":"服务民族复兴", "D":"维护国家主权、安全、发展利益"}, "answer": "D"}, # [cite: 29]
    {"id": "16_s12", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 12, "question": "12.我们将秉持（  ）的全球治理观，积极参与全球治理体系改革和建设。", "options": {"A":"相互尊重", "B":"公平正义", "C":"合作共赢", "D":"共商共建共享"}, "answer": "D"}, # [cite: 29]
    {"id": "16_s13", "type": "single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 13, "question": "13. (  )，是全人类的共同价值，也是联合国的崇高目标。目标远未完成，我们仍须努力。", "options": {"A":"经济、安全、公平、正义、合作、共赢", "B":"和平、发展、公平、正义、民主、自由", "C":"和平、发展、合作、开放、民主、自由", "D":"经济、发展、合作、包容、民主、共赢"}, "answer": "B"}, # [cite: 29, 30]
    # Multiple Choice (多项选择题) from 16.doc
    {"id": "16_m1", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 1, "question": "1.坚持以（   ）为基础走和平发展道路。", "options": {"A":"不冲突不对抗", "B":"相互尊重", "C":"人文交流", "D":"合作共赢"}, "answer": "BD"}, # [cite: 30]
    {"id": "16_m2", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 2, "question": "2.运筹好大国关系，推动构建总体稳定、均衡发展的大国关系框架至关重要。大国之间相处，要（  ）。", "options": {"A":"不冲突", "B":"不对抗", "C":"相互尊重", "D":"合作共赢"}, "answer": "ABCD"}, # [cite: 30]
    {"id": "16_m3", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 3, "question": "3.和平与发展仍然是当今时代主题，（  ）成为不可阻挡的时代潮流。", "options": {"A":"和平", "B":"发展", "C":"合作", "D":"共赢"}, "answer": "ABCD"}, # [cite: 30]
    {"id": "16_m4", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 4, "question": "4.当今世界正经历百年未有之大变局，具体表现在（）。", "options": {"A":"世界多极化、经济全球化、社会信息化、文化多样化深入发展", "B":"世界面临的不稳定性不确定性突出，全球性问题加剧", "C":"国际力量对比深刻变化", "D":"新一轮科技革命和产业变革深入发展", "E":"国际体系和国际秩序深度调整"}, "answer": "ABCDE"}, # [cite: 30]
    {"id": "16_m5", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 5, "question": "5.中国走和平发展道路的自信和自觉（  ）。", "options": {"A":"来源于中华文明的深厚渊源", "B":"来源于对现实中国发展目标条件的认知", "C":"来源于对世界发展大势的把握", "D":"来源于和平发展的大局"}, "answer": "ABC"}, # [cite: 30]
    {"id": "16_m6", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 6, "question": "6.中国特色大国外交建立在正确的（   ）基础之上。", "options": {"A":"历史观", "B":"大局观", "C":"角色观", "D":"国际形势"}, "answer": "ABC"}, # [cite: 30]
    {"id": "16_m7", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 7, "question": "7.中国特色大国外交要坚持的原则要求是（  ）。", "options": {"A":"坚持和加强党对对外工作的集中统一领导", "B":"坚持以中国特色社会主义为根本，增强战略自信", "C":"坚持以相互尊重、合作共赢为基础，走和平发展道路", "D":"坚持以公平正义为理念引领全球治理体系改革", "E":"坚持以国家核心利益为底线维护国家主权、安全、发展利益"}, "answer": "ABCDE"}, # [cite: 30]
    {"id": "16_m8", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 8, "question": "8.中国特色大国外交的独特风范表现在（  ）。", "options": {"A":"坚持马克思主义立场观点方法,从中华优秀传统文化中汲取智慧", "B":"坚持爱国主义同国际主义相结合", "C":"倡导不同社会制度和发展道路相互包容", "D":"坚持诚信为本，始终恪守政治承诺", "E":"倡导不同国家、不同民族、不同文明互学互鉴"}, "answer": "ABCDE"}, # [cite: 30]
    {"id": "16_m9", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 9, "question": "9.我国走和平发展道路，是（ ）。", "options": {"A":"对国际社会关注中国发展走向的回应", "B":"中国人民对实现自身发展目标的自信和自觉", "C":"由中国共产党性质宗旨和我国社会主义制度决定的", "D":"基于中国历史文化传统作出的必然选择", "E":"符合历史潮流、顺应世界大势的正确选择"}, "answer": "ABCDE"}, # [cite: 30]
    {"id": "16_m10", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 10, "question": "10.我国独立自主的和平外交政策的内容包括（  ）。", "options": {"A":"中国始终根据事情本身的是非曲直决定自己的立场和政策", "B":"中国尊重各国主权和领土完整，尊重各国人民选择的发展道路和社会制度", "C":"坚决反对一切形式的範权主义和强权政治", "D":"反对冷战思维，反对干涉别国内政，反对搞双重标准", "E":"奉行防御性的国防政策，中国永远不称霸、永远不搞扩张"}, "answer": "ABCDE"}, # [cite: 30]
    {"id": "16_m11", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 11, "question": "11.新型国际关系的内容是（   ）。", "options": {"A":"相互尊重", "B":"公平正义", "C":"合作共赢", "D":"和平共处"}, "answer": "ABC"}, # [cite: 30, 31]
    {"id": "16_m12", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 12, "question": "12.积极推动中美关系稳定发展，同俄罗斯发展全面战略协作伙伴关系，同欧洲发展（  ）伙伴关系。", "options": {"A":"和平", "B":"增长", "C":"改革", "D":"文明"}, "answer": "ABCD"}, # [cite: 31]
    {"id": "16_m13", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 13, "question": "13.构建人类命运共同体，其核心就是建设持久和平、（  ）的世界。", "options": {"A":"清洁美丽", "B":"普遍安全", "C":"共同繁荣", "D":"开放包容"}, "answer": "ABCD"}, # [cite: 31]
    {"id": "16_m14", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 14, "question": "14.对构建人类命运共同体是世界各国人民前途所在的正确理解是（ ）。", "options": {"A":"构建人类命运共同体是我们党审视当今世界发展趋势、针对当今世界面临的重大问题提出的重要理念", "B":"各国相互联系更紧密，和平、发展、合作、共赢的历史潮流不可阻挡", "C":"全球发展深层次矛盾突出，恃强凌弱、零和博弈等霸凌行径危害深重", "D":"和平赤字、发展赤字、安全赤字、治理赤字加重", "E":"构建人类命运共同体理念为人类社会实现共同发展绘制了蓝图，具有重大而深远的意义"}, "answer": "ABCDE"}, # [cite: 31]
    {"id": "16_m15", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 15, "question": "15.对推进全球治理体系改革和建设的正确理解是（   ）。", "options": {"A":"这是构建人类命运共同体的内在要求", "B":"要秉持共商共建共享的全球治理观", "C":"要推动全球治理体系朝着更加公正合理的方向发展", "D":"要奉行双赢、多赢、共赢的新理念，摒弃冷战思维、零和博弈的旧理念", "E":"坚持真正的多边主义，反对搞意识形态划线"}, "answer": "ABCDE"}, # [cite: 31]
    {"id": "16_m16", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 16, "question": "16.对共建“一带一路”的正确理解是（    ）。", "options": {"A":"共建“一带一路”是推动构建人类命运共同体的实践平台", "B":"“一带一路”倡议根植历史、更面向未来，源于中国、更属于世界", "C":"共建“一带一路”追求的是发展，崇尚的是共赢，传递的是希望", "D":"共建“一带一路”是造福沿线各国人民的大事业", "E":"共建“一带一路”不以意识形态划界，是各方共同打造的国际公共产品"}, "answer": "ABCDE"}, # [cite: 31]
    {"id": "16_m17", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 17, "question": "17.坚持真正的多边主义，完善全球治理体系,要（  ）。", "options": {"A":"坚持协商合作，不搞冲突对抗", "B":"坚持以联合国宪章宗旨和原则为基础的国际关系基本准则，反对搞意识形态划线", "C":"推动共同发展，维护世界和平稳定", "D":"反对搞针对特定国家的阵营化和排他性小圈子", "E":"反对一切形式的单边主义、脱钩、断供等错误做法"}, "answer": "ABCDE"}, # [cite: 31]
    # Judgment (判断题) from 16.doc
    {"id": "16_j1", "type": "judgment_as_single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 1, "question": "1.中国走和平发展道路，不是权宜之计,更不是外交辞令，而是从历史、现实、未来的客观判断中得出的结论,是思想自信和实践自觉的有机统一。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 31]
    {"id": "16_j2", "type": "judgment_as_single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 2, "question": "2.周边是我国安身立命之所、发展繁荣之基。无论从地理方位、自然环境还是相互关系看，周边对我国都具有极为重要的战略意义。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 31]
    {"id": "16_j3", "type": "judgment_as_single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 3, "question": "3. 中国外交秉持真实亲诚理念和正确义利观，加强同周边国家的团结合作。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 31] # "真实亲诚"是周边外交理念，"正确义利观"是处理与发展中国家关系的原则，题目表述可能不完全准确，但答案给了错误。
    {"id": "16_j4", "type": "judgment_as_single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 4, "question": "4.中国外交秉持亲诚惠容的周边外交理念，着力深化互利共嬴格局，找准同周边国家互利合作的战略契合点，构建区域经济一体化新格局。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 31, 32]
    {"id": "16_j5", "type": "judgment_as_single", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 5, "question": "5. 中国外交秉持求同存异、相互尊重、互学互鉴理念，构建新型政党关系。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 32]

    # --- Document 17.doc (doc_order: 17) ---
    # Single Choice (单项选择题)
    {"id": "17_s1", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 1, "question": "1.全面建设社会主义现代化国家、全面推进中华民族伟大复兴，关键在党，关键在（   ）。", "options": {"A":"党中央", "B":"高质量发展", "C":"全面从严治党", "D":"维护党中央权威"}, "answer": "C"}, # [cite: 33]
    {"id": "17_s2", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 2, "question": "2.坚持党要管党、全面从严治党，以党的（  ）为统领。", "options": {"A":"政治建设", "B":"思想建设", "C":"组织建设", "D":"作风建设"}, "answer": "A"}, # [cite: 33]
    {"id": "17_s3", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 3, "question": "3.党的十九大强调，党的（   ）是党的根本性建设，要摆在首位。", "options": {"A":"政治建设", "B":"思想建设", "C":"组织建设", "D":"作风建设"}, "answer": "A"}, # [cite: 33]
    {"id": "17_s4", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 4, "question": "4.经过不懈努力，党找到了（  ）这一跳出治乱兴衰历史周期率的第二个答案，确保党永远不变质、不变色、不变味。", "options": {"A":"新发展理念", "B":"自我革命", "C":"自我完善", "D":"总体国家安全观"}, "answer": "B"}, # [cite: 33, 34]
    {"id": "17_s5", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 5, "question": "5.（  ）是我们党区别于其他政党的显著标志", "options": {"A":"勇于自我革命", "B":"勇于创新", "C":"勇于挑战", "D":"勇于突破"}, "answer": "A"}, # [cite: 34]
    {"id": "17_s6", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 6, "question": "6.（   ）是党的建设的一贯要求和根本方针。", "options": {"A":"勇于自我革命", "B":"党要管党、从严治党", "C":"与时俱进", "D":"“四个意识”和“两个维护”"}, "answer": "B"}, # [cite: 34]
    {"id": "17_s7", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 7, "question": "7.（  ）是党的政治建设的首要任务。", "options": {"A":"增强“四个意识”", "B":"贯彻“四个全面”", "C":"学习贯彻习近平新时代中国特色社会主义思想", "D":"保证全党服从中央，维护党中央权威和集中统一领导"}, "answer": "D"}, # [cite: 34]
    {"id": "17_s8", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 8, "question": "8.（   ）是党的基础性建设。", "options": {"A":"政治建设", "B":"思想建设", "C":"制度建设", "D":"作风建设"}, "answer": "B"}, # [cite: 34]
    {"id": "17_s9", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 9, "question": "9.新中国成立以来，中国共产党人提出跳出历史周期率的两个答案是（  ）。", "options": {"A":"自力更生；艰苦奋斗", "B":"让人民来监督政府；自我革命", "C":"实现四个现代化和实现中华民族伟大复兴", "D":"以经济建设为中心；改革开放"}, "answer": "B"}, # [cite: 34, 35]
    {"id": "17_s10", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 10, "question": "10.坚持和加强党的全面领导，坚持党要管党、全面从严治党，以（ ）为主线。", "options": {"A":"加强党的长期执政能力建设、先进性和纯洁性建设", "B":"党的政治建设", "C":"坚定理想信念宗旨", "D":"调动全党积极性、主动性、创造性"}, "answer": "A"}, # [cite: 35]
    {"id": "17_s11", "type": "single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 11, "question": "11.(    )就是要坚定理想信念宗旨，自觉抵御各种腐朽思想侵蚀，提高政治免疫力，清除一切侵蚀党的健康肌体的病毒。", "options": {"A":"自我净化", "B":"自我完善", "C":"自我革新", "D":"自我提高"}, "answer": "A"}, # [cite: 35]
    # Multiple Choice (多项选择题) from 17.doc
    {"id": "17_m1", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 1, "question": "1.习近平关于党的建设的重要思想，包括（   ）。", "options": {"A":"坚持和加强党的全面领导；坚持以党的自我革命引领社会革命", "B":"坚持以党的政治建设统领党的建设各项工作；坚持江山就是人民、人民就是江山", "C":"坚持思想建党、理论强党；坚持严密党的组织体系", "D":"坚持造就忠诚干净担当的高素质干部队伍；坚持聚天下英才而用之", "E":"坚持持之以恒正风肃纪；坚持一体推进不敢腐、不能腐、不想腐"}, "answer": "ABCDE"}, # [cite: 35]
    {"id": "17_m2", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 2, "question": "2.新形势下党执政面临的“四大考验”包括长期执政考验、（  ）", "options": {"A":"改革开放考验", "B":"市场经济考验", "C":"外部环境考验", "D":"管党治党考验"}, "answer": "ABC"}, # [cite: 35]
    {"id": "17_m3", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 3, "question": "3.新形势下党执政面临的“四大危险”包括精神懈怠危险、（  ）", "options": {"A":"能力不足危险", "B":"脱离群众危险", "C":"消极腐败危险", "D":"动力不足考验"}, "answer": "ABC"}, # [cite: 35, 36]
    {"id": "17_m4", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 4, "question": "4.加强党的自身建设是（   ）。", "options": {"A":"把党锻造成为坚强有力的马克思主义执政党的迫切需要", "B":"新形势下推进伟大事业的必然要求", "C":"新形势下推进进行伟大斗争的必然要求", "D":"新形势下推进实现伟大梦想的必然要求"}, "answer": "ABCD"}, # [cite: 36]
    {"id": "17_m5", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 5, "question": "5.全面从严治党，关键在严，“关键在严”，就是（  ）。", "options": {"A":"坚持严字当头，把严的要求贯穿党的建设全过程", "B":"做到真管真严、敢管敢严、长管长严", "C":"敢于动真格，不降标准，不图形式，不走过场", "D":"让一切违纪违规的言行无处遁形"}, "answer": "ABCD"}, # [cite: 36]
    {"id": "17_m6", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 6, "question": "6.全面从严治党，“要害在治”，就是（ ）。", "options": {"A":"要真正解决问题、切实担起责任", "B":"从党中央到地方各级党委都要担负起主体责任", "C":"各级纪委要担负起监督责任", "D":"敢于瞪眼黑脸，勇于执纪问责", "E":"坚持标本兼治，拔“烂树”、治“病树”、正“歪树”"}, "answer": "ABCDE"}, # [cite: 36]
    {"id": "17_m7", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 7, "question": "7.全面从严治党是一项管党治党的系统工程，要（  ）。", "options": {"A":"坚持内容上全涵盖，党的建设推进到哪里，全面从严治党体系就要构建到哪里", "B":"坚持对象上全覆盖，面向党的各级组织和全体党员", "C":"坚持责任上全链条,让每名党员、干部行使应有权利、履行应尽责任", "D":"坚持制度上全贯通，把制度建设要求体现到全面从严治党全过程"}, "answer": "ABCD"}, # [cite: 36]
    {"id": "17_m8", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 8, "question": "8.新时代党的建设总要求,包括（   ）。", "options": {"A":"坚持和加强党的全面领导，坚持党要管党、全面从严治党", "B":"以加强党的长期执政能力建设、先进性和纯洁性建设为主线", "C":"以党的政治建设为统领，以坚定理想信念宗旨为根基，全面推进党的各项建设", "D":"把制度建设贯穿其中，深入推进反腐败斗争", "E":"把党建设成为人民衷心拥护、勇于自我革命的马克思主义执政党"}, "answer": "ABCDE"}, # [cite: 36]
    {"id": "17_m9", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 9, "question": "9.加强作风建设，必须（  ）。", "options": {"A":"紧紧围绕保持党同人民群众的血肉联系，增强群众观念和群众感情", "B":"要锲而不舍落实中央八项规定精神，持续深化纠治“四风”", "C":"要弘扬党的光荣传统和优良作风", "D":"促进党员干部特别是领导干部带头深入调查研究", "E":"要推进作风建设常态化长效化"}, "answer": "ABCDE"}, # [cite: 36]
    {"id": "17_m10", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 10, "question": "10.我们党之所以勇于自我革命，是因为（   ）。", "options": {"A":"我们党除了国家、民族、人民的利益，没有任何自己的特殊利益", "B":"我们党有高度的自信，勇于坚持真理、修正错误", "C":"我们党立志于中华民族千秋伟业，始终坚守初心使命", "D":"以上都正确"}, "answer": "ABCD"}, # [cite: 36]
    {"id": "17_m11", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 11, "question": "11.党的二十大报告指出，中国共产党立志于中华民族千秋伟业，致力于人类和平与发展崇高事业，全党同志要始终牢记“三个务必”，这“三个务必”是（     ）。", "options": {"A":"务必不忘初心、牢记使命", "B":"务必谦虚谨慎、艰苦奋斗", "C":"务必贯彻好群众路线", "D":"务必敢于斗争、善于斗争"}, "answer": "ABD"}, # [cite: 36]
    {"id": "17_m12", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 12, "question": "12.党的十八大以来，我们坚持党要管党、全面从严治党，坚持问题导向，以整治“四风”为突破口，“四风”包括：形式主义、（ ）", "options": {"A":"官僚主义", "B":"享乐主义", "C":"奢靡之风", "D":"利己主义"}, "answer": "ABC"}, # [cite: 36, 37]
    {"id": "17_m13", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 13, "question": "13.我们要落实新时代党的建设总要求，健全全面从严治党体系，全面推进党的（   ）", "options": {"A":"自我净化", "B":"自我完善", "C":"自我革新", "D":"自我提高"}, "answer": "ABCD"}, # [cite: 37]
    {"id": "17_m14", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 14, "question": "14.坚决打赢反腐败斗争攻坚战持久战，必须清醒认识到，腐败和反腐败较量还在激烈进行，必须（  ）。", "options": {"A":"坚持以零容忍态度反腐惩恶不动摇", "B":"要坚决惩治不收敛不收手、胆大妄为者", "C":"坚决查处政治问题和经济问题交织的腐败", "D":"坚决防止领导干部成为利益集团和权势团体的代言人、代理人", "E":"坚决防止政商勾连、资本向政治领域渗透等破坏政治生态和经济发展环境的腐败"}, "answer": "ABCDE"}, # [cite: 37]
    {"id": "17_m15", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 15, "question": "15.党的十八大以来，以习近平同志为核心的党中央坚持以雷霆之势惩治腐败，走出一条依靠制度优势、法治优势反腐败之路，具体表现在（  ）。", "options": {"A":"构建起党全面领导的反腐败工作格局", "B":"“打虎”“拍蝇”“猎狐”多管齐下", "C":"把权力关进制度的笼子里", "D":"坚持不敢腐、不能腐、不想腐一体推进", "E":"依靠理想信念教育作为反腐败的根本举措"}, "answer": "ABCD"}, # [cite: 37]
    # Document 17, multiple choice questions 16 and 17 are missing options in the provided text.
    # Assuming question 16: "中国共产党是世界上最大的马克思主义执政党，解决大党独有难题，要（ ）。"
    # Assuming question 17: "之所以要把党的政治建设摆在首位，是因为（   ）。"
    # Judgment (判断题) from 17.doc
    {"id": "17_j1", "type": "judgment_as_single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 1, "question": "1.党的自我革命是跳出历史周期率的第一个答案。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 37]
    {"id": "17_j2", "type": "judgment_as_single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 2, "question": "2. 政治建设是党永葆生机活力、走好新的赶考之路的必由之路。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 37]
    {"id": "17_j3", "type": "judgment_as_single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 3, "question": "3. 要以伟大社会革命引领伟大自我革命，以伟大自我革命促进伟大社会革命，确保党在新时代坚持和发展中国特色社会主义的历史进程中始终成为坚强领导核心。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 37] # Original is "错误", text says to lead great social revolution with great self-revolution. The reverse seems to be the correct statement often.
    {"id": "17_j4", "type": "judgment_as_single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 4, "question": "4.党的自我革命，就是要永不僵化、永不停滞，在学习实践中砥砺品格、增长才干，全面增强执政本领，不断提升政治境界、思想境界、道德境界，永葆党的生机活力。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 37] # This describes self-improvement/self-enhancement, not specifically self-renewal/innovation as the sole definition.
    {"id": "17_j5", "type": "judgment_as_single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 5, "question": "5.全面从严治党，核心是加强党的领导，基础在全面，关键在严，要害在治。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 37]
    {"id": "17_j6", "type": "judgment_as_single", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 6, "question": "6.党的政治建设是根本性建设，决定党的建设的方向和效果，只有党的政治建设抓好了，党的建设才能夯基固本。", "options": {"A": "正确", "B": "错误"}, "answer": "A"} # [cite: 37]
]

# Let me load this from the original file to ensure we have all questions
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# We'll define the complete question dataset here
# This will be populated with all 400+ questions from the original application

# --- 路由定义 ---
@app.route('/')
def home():
    # 检查用户是否已登录
    if 'user_id' in session:
        return redirect(url_for('quiz_page_actual'))
    # 如果未登录，重定向到登录页面
    return redirect(url_for('login_page'))

@app.route('/quiz')
def quiz_page_actual():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    return render_template('quiz_website.html', 
                           username=session.get('username'),
                           all_questions_from_server=ALL_QUESTION_DATA_PYTHON)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': '用户名和密码不能为空！'}), 400

        try:
            # 查找用户
            user = db_manager.execute_query(
                "SELECT * FROM users WHERE username = %s" if db_manager.is_postgres else "SELECT * FROM users WHERE username = ?",
                (username,),
                fetch_one=True
            )

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return jsonify({'message': '登录成功！', 'redirect_url': url_for('quiz_page_actual')}), 200
            else:
                return jsonify({'message': '用户名或密码错误！'}), 401
        except Exception as e:
            logger.error(f"登录失败: {e}")
            return jsonify({'message': '登录失败，请稍后重试'}), 500
    
    if 'user_id' in session:
        return redirect(url_for('quiz_page_actual'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        logger.info("收到注册请求")
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"注册用户名: {username}")

        if not username or not password:
            logger.warning("用户名或密码为空")
            return jsonify({'message': '用户名和密码不能为空！'}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        logger.info(f"密码已哈希")
        
        try:
            # 插入新用户
            db_manager.execute_query(
                "INSERT INTO users (username, password) VALUES (%s, %s)" if db_manager.is_postgres else "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            
            logger.info(f"用户 {username} 注册成功")
            return jsonify({'message': '注册成功！请登录。'}), 201
            
        except Exception as e:
            logger.error(f"注册失败: {e}")
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                return jsonify({'message': '用户名已存在！'}), 409
            else:
                return jsonify({'message': '注册失败，请稍后重试'}), 500
        
    return render_template('register.html')

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return jsonify({'message': '登出成功！', 'redirect_url': url_for('login_page')}), 200

# --- 错题本功能路由 ---
@app.route('/api/submit_answer', methods=['POST'])
def submit_answer():
    """提交答案API，记录错题"""
    if 'user_id' not in session:
        return jsonify({'message': '请先登录'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        question_id = data.get('question_id')
        user_answer = data.get('user_answer')
        correct_answer = data.get('correct_answer')
        question_data = data.get('question_data')
        
        if not all([question_id, user_answer, correct_answer, question_data]):
            return jsonify({'message': '缺少必要参数'}), 400
        
        # 如果答错了，记录到错题本
        if user_answer != correct_answer:
            db_manager.add_wrong_answer(
                user_id=user_id,
                question_id=question_id,
                question_text=question_data.get('question', ''),
                question_type=question_data.get('type', ''),
                correct_answer=correct_answer,
                user_answer=user_answer,
                question_options=question_data.get('options', {}),
                source_doc=question_data.get('source_doc', '')
            )
            return jsonify({'correct': False, 'message': '答案错误，已记录到错题本'}), 200
        else:
            # 答对了，检查是否需要标记错题为已纠正
            db_manager.mark_question_corrected(user_id, question_id)
            return jsonify({'correct': True, 'message': '答案正确！'}), 200
            
    except Exception as e:
        logger.error(f"提交答案失败: {e}")
        return jsonify({'message': '提交失败，请稍后重试'}), 500

@app.route('/wrong_answers')
def wrong_answers_page():
    """错题本页面"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    try:
        user_id = session['user_id']
        wrong_answers = db_manager.get_wrong_answers(user_id)
        stats = db_manager.get_wrong_answer_stats(user_id)
        
        return render_template('wrong_answers.html', 
                             username=session.get('username'),
                             wrong_answers=wrong_answers,
                             stats=stats)
    except Exception as e:
        logger.error(f"获取错题本失败: {e}")
        return redirect(url_for('quiz_page_actual'))

@app.route('/retry_wrong_questions')
def retry_wrong_questions():
    """重做错题"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    try:
        user_id = session['user_id']
        wrong_answers = db_manager.get_wrong_answers(user_id)
        
        # 构建错题的question数据格式
        wrong_questions = []
        for wa in wrong_answers:
            import json
            question_data = {
                'id': wa['question_id'] if 'question_id' in wa else wa[2],
                'type': wa['question_type'] if 'question_type' in wa else wa[4],
                'question': wa['question_text'] if 'question_text' in wa else wa[3],
                'options': json.loads(wa['question_options'] if 'question_options' in wa else wa[7]) if (wa['question_options'] if 'question_options' in wa else wa[7]) else {},
                'answer': wa['correct_answer'] if 'correct_answer' in wa else wa[5],
                'source_doc': wa['source_doc'] if 'source_doc' in wa else wa[8]
            }
            wrong_questions.append(question_data)
        
        return render_template('quiz_website.html', 
                             username=session.get('username'),
                             all_questions_from_server=wrong_questions,
                             mode='retry')
    except Exception as e:
        logger.error(f"重做错题失败: {e}")
        return redirect(url_for('wrong_answers_page'))

@app.route('/api/mark_corrected', methods=['POST'])
def mark_corrected():
    """标记错题为已纠正"""
    if 'user_id' not in session:
        return jsonify({'message': '请先登录'}), 401
    
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        
        if not question_id:
            return jsonify({'message': '缺少题目ID'}), 400
        
        user_id = session['user_id']
        db_manager.mark_question_corrected(user_id, question_id)
        
        return jsonify({'message': '已标记为纠正'}), 200
        
    except Exception as e:
        logger.error(f"标记纠正失败: {e}")
        return jsonify({'message': '操作失败，请稍后重试'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点，用于验证应用和数据库状态"""
    try:
        # 检查用户数量
        result = db_manager.execute_query(
            "SELECT COUNT(*) as count FROM users",
            fetch_one=True
        )
        user_count = result['count'] if result else 0
        
        status = {
            "status": "healthy",
            "database_type": "PostgreSQL" if db_manager.is_postgres else "SQLite",
            "user_count": user_count,
            "working_directory": os.getcwd(),
            "environment": {
                "DATABASE_URL": "configured" if os.environ.get('DATABASE_URL') else "not set",
                "RENDER": os.environ.get('RENDER', 'Not set'),
                "RAILWAY_ENVIRONMENT": os.environ.get('RAILWAY_ENVIRONMENT', 'Not Set'),
                "PORT": os.environ.get('PORT', 'Not set')
            }
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "working_directory": os.getcwd()
        }), 500

@app.route('/debug/users', methods=['GET'])
def debug_users():
    """调试端点：查看用户列表（仅用于验证，生产环境应该移除）"""
    try:
        # 获取所有用户（隐藏密码）
        users = db_manager.execute_query(
            "SELECT id, username FROM users ORDER BY id",
            fetch_all=True
        )
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user['id'],
                "username": user['username']
            })
        
        return jsonify({
            "total_users": len(user_list),
            "users": user_list,
            "database_type": "PostgreSQL" if db_manager.is_postgres else "SQLite"
        }), 200
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        return jsonify({
            "error": str(e)
        }), 500

# 章节和题型映射
CHAPTER_MAPPING = {
    '导论': {'display_name': '导论', 'doc_order': 0},
    '01': {'display_name': '第一章', 'doc_order': 1},
    '02': {'display_name': '第二章', 'doc_order': 2},
    '03': {'display_name': '第三章', 'doc_order': 3},
    '04': {'display_name': '第四章', 'doc_order': 4},
    '05': {'display_name': '第五章', 'doc_order': 5},
    '06': {'display_name': '第六章', 'doc_order': 6},
    '07': {'display_name': '第七章', 'doc_order': 7},
    '08': {'display_name': '第八章', 'doc_order': 8},
    '09': {'display_name': '第九章', 'doc_order': 9},
    '10': {'display_name': '第十章', 'doc_order': 10},
    '11': {'display_name': '第十一章', 'doc_order': 11},
    '12': {'display_name': '第十二章', 'doc_order': 12},
    '13': {'display_name': '第十三章', 'doc_order': 13},
    '14': {'display_name': '第十四章', 'doc_order': 14},
    '15': {'display_name': '第十五章', 'doc_order': 15},
    '16': {'display_name': '第十六章', 'doc_order': 16},
    '17': {'display_name': '第十七章', 'doc_order': 17}
}

TYPE_MAPPING = {
    'single': '单项选择题',
    'multiple': '多项选择题', 
    'judgment_as_single': '判断题'
}

def get_chapter_statistics():
    """获取各章节统计信息"""
    chapter_stats = {}
    
    for question in ALL_QUESTION_DATA_PYTHON:
        # 解析章节
        source_doc = question.get('source_doc', '')
        if source_doc == '导论.doc':
            chapter = '导论'
        else:
            # 提取章节号，如 "01.doc" -> "01"
            chapter = source_doc.replace('.doc', '')
        
        if chapter not in chapter_stats:
            chapter_stats[chapter] = {
                'name': chapter,
                'display_name': CHAPTER_MAPPING.get(chapter, {}).get('display_name', chapter),
                'total_questions': 0,
                'accuracy_rate': 85.0  # 默认正确率，实际应该从用户历史记录计算
            }
        
        chapter_stats[chapter]['total_questions'] += 1
    
    return list(chapter_stats.values())

def get_questions_by_chapter_and_type(chapter, question_type=None):
    """根据章节和题型筛选题目"""
    filtered_questions = []
    
    for question in ALL_QUESTION_DATA_PYTHON:
        # 匹配章节
        source_doc = question.get('source_doc', '')
        if chapter == '导论' and source_doc == '导论.doc':
            chapter_match = True
        elif chapter != '导论' and source_doc == f'{chapter}.doc':
            chapter_match = True
        else:
            chapter_match = False
        
        # 匹配题型
        if question_type and question.get('type') != question_type:
            type_match = False
        else:
            type_match = True
        
        if chapter_match and type_match:
            filtered_questions.append(question)
    
    return filtered_questions

def get_chapter_question_types(chapter):
    """获取指定章节的题型统计"""
    type_stats = {}
    questions = get_questions_by_chapter_and_type(chapter)
    
    for question in questions:
        q_type = question.get('type')
        if q_type not in type_stats:
            type_stats[q_type] = {
                'type': q_type,
                'display_name': TYPE_MAPPING.get(q_type, q_type),
                'count': 0
            }
        type_stats[q_type]['count'] += 1
    
    return list(type_stats.values())

@app.route('/chapter_practice')
@app.route('/chapter_practice/<chapter>')
@app.route('/chapter_practice/<chapter>/<type>')
def chapter_practice(chapter=None, type=None):
    """章节练习页面"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    try:
        # 如果没有选择章节，显示章节列表
        if not chapter:
            chapters = get_chapter_statistics()
            return render_template('chapter_practice.html',
                                 username=session.get('username'),
                                 chapters=chapters,
                                 selected_chapter=None,
                                 selected_type=None)
        
        # 如果选择了章节但没有选择题型，显示题型列表
        if chapter and not type:
            question_types = get_chapter_question_types(chapter)
            chapter_name = CHAPTER_MAPPING.get(chapter, {}).get('display_name', chapter)
            return render_template('chapter_practice.html',
                                 username=session.get('username'),
                                 selected_chapter=chapter,
                                 selected_chapter_name=chapter_name,
                                 question_types=question_types,
                                 selected_type=None)
        
        # 如果选择了章节和题型，开始练习
        if chapter and type:
            questions = get_questions_by_chapter_and_type(chapter, type)
            chapter_name = CHAPTER_MAPPING.get(chapter, {}).get('display_name', chapter)
            type_name = TYPE_MAPPING.get(type, type)
            
            return render_template('chapter_practice.html',
                                 username=session.get('username'),
                                 selected_chapter=chapter,
                                 selected_chapter_name=chapter_name,
                                 selected_type=type,
                                 selected_type_name=type_name,
                                 questions=questions)
                                 
    except Exception as e:
        logger.error(f"章节练习页面错误: {e}")
        return redirect(url_for('quiz_page_actual'))

@app.route('/api/record_wrong_answer', methods=['POST'])
def record_wrong_answer():
    """记录错题API"""
    if 'user_id' not in session:
        return jsonify({'message': '请先登录'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        db_manager.add_wrong_answer(
            user_id=user_id,
            question_id=data['question_id'],
            question_text=data['question_text'],
            question_type=data['question_type'],
            correct_answer=data['correct_answer'],
            user_answer=data['user_answer'],
            question_options=data['question_options'],
            source_doc=data['source_doc']
        )
        
        return jsonify({'message': '错题记录成功'}), 200
        
    except Exception as e:
        logger.error(f"记录错题失败: {e}")
        return jsonify({'message': '记录错题失败'}), 500

# Main execution block to start the Flask development server
if __name__ == '__main__':
    try:
        # Initialize the database
        logger.info("Initializing database...")
        db_manager.init_database()
        logger.info("Database initialized successfully")
        
        # Start the Flask development server
        logger.info(f"Starting Flask application on port {PORT}...")
        app.run(host='0.0.0.0', port=PORT, debug=True)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

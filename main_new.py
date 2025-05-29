from flask import Flask, render_template, url_for, request, jsonify, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
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
    # --- Document 01.doc (doc_order: 1) ---
    # Single Choice (单项选择题)
    {"id": "01_s1", "type": "single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 1, "question": "1.中国特色社会主义道路是（ ）。", "options": {"A": "实现途径", "B": "行动指南", "C": "根本保障", "D": "精神力量"}, "answer": "A"}, #
    {"id": "01_s2", "type": "single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 2, "question": "2.（ ）宣布，中国特色社会主义进入了新时代，这是我国发展新的历史方位。", "options": {"A": "党的十八大", "B": "党的二十大", "C": "党的十七大", "D": "党的十九大"}, "answer": "D"}, #
    {"id": "01_s3", "type": "single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 3, "question": "3. 习近平总书记在十九大报告中指出，中国特色社会主义进入新时代，我国社会主要矛盾（ ）。", "options": {"A":"已经转化为人民日益增长的美好生活需要和不平衡不充分的发展之间的矛盾", "B":"仍然是无产阶级同资产阶级之间的矛盾", "C":"官僚资本同民族资本之间的矛盾", "D":"是人民日益增长的物质文化需要同落后的社会生产之间的矛盾。"}, "answer": "A"}, #
    {"id": "01_s4", "type": "single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 4, "question": "4.（ ）是坚持和发展中国特色社会主义的行动指南。", "options": {"A": "党的基本路线", "B":"党的基本理论", "C":"党的基本方略", "D":"党的基本政策"}, "answer": "B"}, #
    {"id": "01_s5", "type": "single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 5, "question": "5.中国共产党为什么能，中国特色社会主义为什么好，归根到底是（）。", "options": {"A":"马克思主义行，是中国化时代化的马克思主义行", "B":"中国共产党能", "C":"中国特色社会主义好", "D":"靠坚持四项基本原则，不犯错误"}, "answer": "A"}, #
    {"id": "01_s6", "type": "single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 6, "question": "6.（）是当代中国发展进步的根本制度保障，具有明显制度优势。", "options": {"A":"中国特色社会主义制度", "B":"中国特色社会主义经济制度", "C":"中国特色社会主义理论体系", "D":"中国特色社会主义道路"}, "answer": "A"}, #
    # Multiple Choice (多项选择题) from 01.doc
    {"id": "01_m1", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 1, "question": "1.中国特色社会主义是（  ）。", "options": {"A":"在改革开放40多年的伟大实践中得来的", "B":"在新中国成立70多年的持续探索中得来的", "C":"在中国共产党领导人民进行伟大社会革命100多年的实践中得来的", "D":"在近代以来中华民族由衰到盛180多年的历史进程中得来的", "E":"在世界社会主义500多年波澜壮阔的发展历程中得来的", "F":"在对中华文明5000多年的传承发展中得来的。"}, "answer": "ABCDEF"}, #
    {"id": "01_m2", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 2, "question": "2.中国特色社会主义坚持科学社会主义基本原则，并赋予其鲜明的中国特色,包括（ ）。", "options": {"A":"坚持人民代表大会制度的根本政治制度", "B":"中国共产党领导的多党合作和政治协商制度", "C":"坚持公有制为主体多种所有制经济共同发展", "D":"坚持按劳分配为主体多种分配方式并存", "E":"坚持社会主义市场经济体制"}, "answer": "ABCDE"}, # # Corrected option E to remove leading space
    {"id": "01_m3", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 3, "question": "3.改革开放以来，我们取得一切成绩和进步的根本原因，就是(   ).", "options": {"A":"开辟了中国特色社会主义道路", "B":"形成了中国特色社会主义理论体系", "C":"确立了中国特色社会主义制度", "D":"发展了中国特色社会主义文化。", "E":"建设社会主义生态文明"}, "answer": "ABCD"}, #
    {"id": "01_m4", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 4, "question": "4.中国特色社会主义制度的根本制度有（  ）。", "options": {"A":"党的领导制度", "B":"人民代表大会制度", "C":"马克思主义指导制度", "D":"基层群众自治制度"}, "answer": "ABC"}, #
    {"id": "01_m5", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 5, "question": "5.中国特色社会主义进入了新时代的判断，是（ ）。", "options": {"A":"基于我国发展进入新阶段的伟大成就", "B":"基于社会主要矛盾发生新变化", "C":"基于党的新的奋斗目标", "D":"基于我国面临新的国际环境。"}, "answer": "ABCD"}, #
    {"id": "01_m6", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 6, "question": "6.中国特色社会主义新时代，（   ）。", "options": {"A":"是承前启后、继往开来，在新的历史条件下继续夺取中国特色社会主义伟大胜利的时代。", "B":"是决胜全面建成小康社会、进而全面建设社会主义现代化强国的时代。", "C":"是全国各族人民团结奋斗、不断创造美好生活、逐步实现全体人民共同富裕的时代.", "D":"全体中华儿女勠力同心、奋力实现中华民族伟大复兴中国梦的时代。"}, "answer": "ABCD"}, #
    {"id": "01_m7", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 7, "question": "7.党的十九大概括中国特色社会主义进入新时代的重大意义,这就是：", "options": {"A":"意味着中华民族迎来了从站起来、富起来到强起来的伟大飞跃，迎来了中华民族伟大复兴的光明前景。", "B":"意味着科学社会主义在中国焕发出强大生机活力，在世界上高高举起了中国特色社会主义伟大旗帜", "C":"意味着中国特色社会主义道路、理论、制度、文化不断发展，拓展了发展中国家实现现代化的途径", "D":"意味着中国即将建成社会主义现代化强国，全体人民过上共同富裕的生活。"}, "answer": "ABC"}, #
    {"id": "01_m8", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 8, "question": "8. 我国社会主要矛盾的变化（   ）。", "options": {"A":"没有改变我们对我国社会主义所处历史阶段的判断", "B":"我国仍处于并将长期处于社会主义初级阶段的基本国情没有变", "C":"我国是世界最大发展中国家的国际地位没有变", "D":"以上都正确"}, "answer": "ABCD"}, #
    {"id": "01_m9", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 9, "question": "9.中国特色社会主义制度，（）。", "options": {"A":"坚持把根本制度、基本制度、重要制度以及各方面体制机制等具体制度有机结合起来", "B":"坚持把国家层面民主制度同基层民主制度有机结合起来", "C":"坚持把党的领导、人民当家作主、依法治国有机结合起来", "D":"既坚持了社会主义的根本性质，又借鉴了古今中外制度建设的有益成果。"}, "answer": "ABCD"}, #
    {"id": "01_m10", "type": "multiple", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 10, "question": "10.中国特色社会主义文化，（）。", "options": {"A":"是激励全党全国各族人民奋勇前进的强大精神力量", "B":"它源自于5000多年文明历史的中华优秀传统文化", "C":"熔铸于党领导人民在革命、建设、改革中创造的革命文化和社会主义先进文化", "D":"植根于中国特色社会主义伟大实践"}, "answer": "ABCD"}, #
    # Judgment (判断题) from 01.doc
    {"id": "01_j1", "type": "judgment_as_single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 1, "question": "1.中国特色社会主义具有深厚的历史渊源和广泛的现实基础，是实现中华民族伟大复兴的正确道路。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "01_j2", "type": "judgment_as_single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 2, "question": "2.坚持和发展中国特色社会主义是一篇大文章，毛泽东同志为它确定了基本思路和基本原则。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, #
    {"id": "01_j3", "type": "judgment_as_single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 3, "question": "3.中国特色社会主义，既坚持了科学社会主义基本原则，又根据时代条件赋予其鲜明的中国特色。这就是说，中国特色社会主义是社会主义，不是别的什么主义。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "01_j4", "type": "judgment_as_single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 4, "question": "4.中国特色社会主义写出了科学社会主义的“新版本”。中国特色社会主义不是简单延续我国历史文化的母版，不是简单套用马克思主义经典作家设想的模板，不是其他国家社会主义实践的再版，也不是国外现代化发展的翻版。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "01_j5", "type": "judgment_as_single", "source_doc": "01.doc", "doc_order": 1, "q_num_in_doc": 5, "question": "5.中国特色社会主义道路是实现途径，理论体系是行动指南，制度是根本保障，文化是精神力量，四者统一于中国特色社会主义伟大实践。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #

    # --- Document 02.doc (doc_order: 2) ---
    # Single Choice (单项选择题)
    {"id": "02_s1", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 1, "question": "1. 一百年来，中国共产党团结带领中国人民进行的一切奋斗、一切牺牲、一切创造，归结起来就是一个主题（ ）。", "options": {"A":"建立新中国", "B":"追求共同富裕", "C":"实现中华民族伟大复兴", "D":"实现人民对美好生活的向往"}, "answer": "C"}, #
    {"id": "02_s2", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 2, "question": "2. 中国梦归根到底是（  ），必须紧紧依靠人民来实现，必须不断为人民造福。", "options": {"A":"国家的梦", "B":"人民的梦", "C":"民族的梦", "D":"世界的梦"}, "answer": "B"}, #
    {"id": "02_s3", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 3, "question": "3.中华民族伟大复兴的中国梦是（   ）相统一的梦。", "options": {"A":"国家情怀、民族情怀、人民情怀", "B":"国家情怀、民族情怀、社会情怀", "C":"民族情怀、世界情怀、人民情怀", "D":"国家情怀、家庭情怀、人民情怀"}, "answer": "A"}, #
    {"id": "02_s4", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 4, "question": "4. 实现中国梦必须走中国道路，这就是（   ）。", "options": {"A":"中华民族大团结之路", "B":"社会发展之路", "C":"人民民主专政之路", "D":"中国特色社会主义道路"}, "answer": "D"}, #
    {"id": "02_s5", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 5, "question": "5. 实现中国梦必须凝聚中国力量，这就是（   ）。", "options": {"A":"各族人民大团结的力量", "B":"中国共产党的领导力量", "C":"中高速增长的经济力量。", "D":"保障有力的军事力量"}, "answer": "A"}, #
    {"id": "02_s6", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 6, "question": "6.(   )首次把“小康”作为经济建设总的奋斗目标。", "options": {"A":"党的十七大", "B":"党的十五大", "C":"党的十二大", "D":"党的十一届三中全会"}, "answer": "C"}, #
    {"id": "02_s7", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 7, "question": "7.（ ）针对当时小康低水平、不全面、发展很不平衡的实际，提出全面建设小康社会目标", "options": {"A":"党的十四大", "B":"党的十六大", "C":"党的十五大", "D":"党的十七大"}, "answer": "B"}, #
    {"id": "02_s8", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 8, "question": "8. 从全面建设社会主义现代化国家进程的阶段安排看来，到2035年，我国将（  ）。", "options": {"A":"全面建成小康社会", "B":"实现中华民族伟大复兴的中国梦", "C":"把我国建设成为富强美丽文明和谐的社会现代化强国。", "D":"基本实现社会主义现代化"}, "answer": "D"}, #
    {"id": "02_s9", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 9, "question": "9.党的十九大提出，到（   ）各方面制度更加完善，国家治理体系和治理能力现代化基本实现。", "options": {"A":"2035年", "B":"2030年", "C":"2025年", "D":"2020年"}, "answer": "A"}, #
    {"id": "02_s10", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 10, "question": "10. 2021年7月1日，习近平在天安门城楼上庄严宣告，经过全党全国各族人民持续奋斗，我们实现了（   ）。", "options": {"A":"第一个百年奋斗目标", "B":"社会主义现代化国家", "C":"社会主义现代化强国", "D":"中华民族伟大复兴"}, "answer": "A"}, #
    {"id": "02_s11", "type": "single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 11, "question": "11.全面建成社会主义现代化强国的战略安排，把基本实现社会主义现代化的时间提前了（  ）年。", "options": {"A":"25年", "B":"15年", "C":"35年", "D":"10年"}, "answer": "B"}, #
    # Multiple Choice (多项选择题) from 02.doc
    {"id": "02_m1", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 1, "question": "1.党的二十大指出，新时代新征程中国共产党的中心任务，就是（ ）。", "options": {"A":"团结带领全国各族人民全面建成社会主义现代化强国", "B":"实现第二个百年奋斗目标", "C":"以中国式现代化全面推进中华民族伟大复兴。", "D":"贯彻新发展理念，促进高质量发展"}, "answer": "ABC"}, #
    {"id": "02_m2", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 2, "question": "2. 坚持和发展中国特色社会主义的总任务是（ ）。", "options": {"A":"解放和发展社会生产力", "B":"实现社会主义现代化和中华民族伟大复兴", "C":"实在全面建成小康社会的基础上，分两步走在本世纪中叶建成富强民主文明和谐美丽的社会主义现代化强国", "D":"中国梦是中华民族伟大复兴的形象表达"}, "answer": "BC"}, #
    {"id": "02_m3", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 3, "question": "3.中国梦的科学内涵是（ ）", "options": {"A":"国家富强", "B":"社会和谐", "C":"民族振兴", "D":"人民幸福"}, "answer": "ACD"}, #
    {"id": "02_m4", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 4, "question": "4.中国梦的实现途径是（ ）。", "options": {"A":"坚持中国道路", "B":"维护世界和平", "C":"弘扬中国精神", "D":"凝聚中国力量"}, "answer": "ACD"}, #
    {"id": "02_m5", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 5, "question": "5.关于中国梦的内涵理解正确的是（）。", "options": {"A":"核心内容时国家富强、民族振兴、人民幸福", "B":"中国梦是国家的梦、民族的梦、归根到底是人民的梦", "C":"国家富强、民族振兴是人民幸福的基础和保障", "D":"人民幸福是国家富强、民族振兴的根本出发点和落脚点"}, "answer": "ABCD"}, #
    {"id": "02_m6", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 6, "question": "6.我们确立了“两个一百年”奋斗目标，就是（  ）。", "options": {"A":"到2020年实现国内生产总值和城乡居民人均收入比2010年翻一番，全面建成小康社会", "B":"到本世纪中叶建成富强民主文明和谐美丽的社会主义现代化国家，实现中华民族伟大复兴", "C":"到2035年，基本建成社会主义现代化国家", "D":"到2025年，实现工业强国目标"}, "answer": "AB"}, #
    {"id": "02_m7", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 7, "question": "7.党的十九大报告中提出全面建设社会主义现代化国家的进程分两个阶段来安排(   )。", "options": {"A":"第一阶段，从2017年到2037年在全面建成小康社会的基础上，再奋斗15年，基本实现社会主义现代化", "B":"第二个阶段，从2037年到本世纪中叶在基本实现现代化的基础上，再奋斗15年，把我国建成富强民主文明和谐美丽的社会主义现代化强国", "C":"第一个阶段，从2020年到2035年，在全面建成小康社会的基础上，再奋斗15年，基本实现社会主义现代化", "D":"第二个阶段，从2035年到本世纪中叶，在基本实现现代化的基础上，再奋斗15年，把我国建成富强民主文明和谐美丽的社会主义现代化强国"}, "answer": "CD"}, #
    {"id": "02_m8", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 8, "question": "8.中国梦是（   ）的梦，与世界各国人民的美好梦想相通。", "options": {"A":"和平", "B":"发展", "C":"合作", "D":"共赢"}, "answer": "ABCD"}, #
    {"id": "02_m9", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 9, "question": "9.（   ），是我们党的初心和使命，是党领导现代化建设的出发点和落脚点，也是新发展理念的“根”和“魂。", "options": {"A":"为人民谋幸福", "B":"为人民谋复兴", "C":"为民族谋复兴", "D":"为民族谋幸福"}, "answer": "AC"}, #
    {"id": "02_m10", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 10, "question": "10..从2020年到2035年，基本实现社会主义现代化的目标要求(   )。", "options": {"A":"在经济建设方面，我国经济实力、科技实力将大幅跃升，跻身创新型国家前列", "B":"在政治建设方面，人民平等参与、平等发展权利得到充分保障，法治国家、法治政府、法治社会基本建成，各方面制度更加完善，国家治理体系和治理能力现代化基本实现", "C":"在文化建设方面，社会文明程度达到新的高度，国家文化软实力显著增强，中华文化影响更加广泛深入", "D":"在生态文明建设方面，生态环境根本好转，美丽中国目标基本实现"}, "answer": "ABCD"}, #
    {"id": "02_m11", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 11, "question": "11. 从2035年到本世纪中叶，建成社会主义现代化强国的目标要求(  )", "options": {"A":"我国将拥有高度的物质文明，社会生产力水平大幅提高，核心竞争力名列世界前茅，经济总量和市场规模超越其他国家", "B":"我国将拥有高度的政治文明，形成又有集中又有民主、又有纪律又有自由、又有统一意志又有个人心情舒畅生动活泼的政治局面，依法治国和以德治国有机结合", "C":"我国将拥有高度的精神文明，践行社会主义核心价值观成为全社会自觉行动，国民素质显著提高，中国精神、中国价值、中国力量成为中国发展的重要影响力和推动力", "D":"我国将拥有高度的社会文明，城乡居民将普遍拥有较高的收入、富裕的生活、健全的基本公共服务"}, "answer": "ABCD"}, #
    {"id": "02_m12", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 12, "question": "12.全面建成了小康社会的重大意义是（   ）。", "options": {"A":"意味着中华民族实现千百年来的夙愿", "B":"表明我国发展和人民生活水平跃上新的大台阶", "C":"表明我国已经实现了由高速发展向高质量发展转变", "D":"是实现中华民族伟大复兴征程中的关键一步"}, "answer": "ABD"}, #
    {"id": "02_m13", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 13, "question": "13.中国式现代化的特征是（     ）。", "options": {"A":"人口规模巨大的现代化", "B":"全体人民共同发展的现代化", "C":"物质文明和精神文明相协调的现代化", "D":"人与自然和谐共生的现代化", "E":"走和平发展道路的现代化"}, "answer": "ACDE"}, # # Typo "共同发展" in source, should be "共同富裕" to be fully aligned with 5 characteristics. However, sticking to source.
    {"id": "02_m14", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 14, "question": "14.中国式现代化（    ）。", "options": {"A":"深深植根于中华优秀传统文化", "B":"体现科学社会主义的先进本质", "C":"借鉴吸收一切人类优秀文明成果", "D":"代表人类文明进步的发展方向", "E":"是一种全新的人类文明形态，但不可复制。"}, "answer": "ABCD"}, #
    {"id": "02_m15", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 15, "question": "15.中国式现代化的本质要求是(    )", "options": {"A":"坚持中国共产党领导", "B":"坚持中国特色社会主义", "C":"实现高质量发展", "D":"发展全过程人民民主", "E":"实现全体人民共同富裕"}, "answer": "ABCDE"}, #
    {"id": "02_m16", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 16, "question": "16.推进中国式现代化需要牢牢把握的重大原则是（）。", "options": {"A":"坚持和加强党的全面领导", "B":"坚持中国特色社会主义道路", "C":"坚持以人民为中心的发展思想", "D":"坚持深化改革开放", "E":"坚持发扬斗争精神"}, "answer": "ABCDE"}, #
    {"id": "02_m17", "type": "multiple", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 17, "question": "17.推进中国式现代化需要正确处理的重大关系是（）。", "options": {"A":"正确处理顶层设计与实践探索的关系", "B":"正确处理战略与策略的关系", "C":"正确处理守正与创新的关系", "D":"正确处理效率与公平的关系", "E":"正确处理独立自主与对外开放的关系"}, "answer": "ABCDE"}, #
    # Judgment (判断题) from 02.doc
    {"id": "02_j1", "type": "judgment_as_single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 1, "question": "1.共同富裕是中国特色社会主义的本质要求，我国很快就实现共同富裕。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, #
    {"id": "02_j2", "type": "judgment_as_single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 2, "question": "2.团结奋斗是中国共产党和中国人民最显著的精神标识，是中国人民创造历史伟业的必由之路。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "02_j3", "type": "judgment_as_single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 3, "question": "3.中国式现代化创造了人类文明新形态，为人类实现现代化提供了新的选择。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "02_j4", "type": "judgment_as_single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 4, "question": "4.独立自主是我们立党立国的重要原则，对外开放是我国的基本国策。推进中国式现代化，必须坚持独立自主、自立自强。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "02_j5", "type": "judgment_as_single", "source_doc": "02.doc", "doc_order": 2, "q_num_in_doc": 5, "question": "5.中国式现代化为广大发展中国家探索现代化道路提供了全新选择。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #

    # --- Document 03.doc (doc_order: 3) ---
    # Single Choice (单项选择题)
    {"id": "03_s1", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 1, "question": "1.习近平指出：“一定要认清，中国最大的国情就是（ ）。什么是中国特色？这就是中国特色。”", "options": {"A":"人口14亿", "B":"中国共产党的领导", "C":"人均GDP世界第二", "D":"吃饭是个山大的问题"}, "answer": "B"}, #
    {"id": "03_s2", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 2, "question": "2.（  ）是党的领导的最高原则，是党保持团结统一和强大战斗力的关键所在。", "options": {"A":"民主集中制", "B":"党中央集中统一领导", "C":"群众路线", "D":"实事求是"}, "answer": "B"}, #
    {"id": "03_s3", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 3, "question": "3. 维护党中央权威和集中统一领导，最关键的是（  ）。", "options": {"A":"坚决维护习近平同志党中央的核心、全党的核心地位", "B":"实行民主集中制", "C":"修改党章，加强党中央权力", "D":"严明政治纪律"}, "answer": "A"}, #
    {"id": "03_s4", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 4, "question": "4.中国共产党是以（   ）为根本组织原则和领导制度。", "options": {"A":"群众路线", "B":"民主集中制", "C":"党章", "D":"政治纪律"}, "answer": "B"}, #
    {"id": "03_s5", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 5, "question": "5.党的领导制度是我国的（   ）制度", "options": {"A":"根本制度", "B":"重要制度", "C":"基本制度", "D":"政策策略"}, "answer": "A"}, #
    {"id": "03_s6", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 6, "question": "6. 坚持党总揽全局、协调各方的领导核心地位，（  ）形象地说，这就像“众星捧月”，这个“月”就是中国共产党。", "options": {"A":"习近平", "B":"邓小平", "C":"毛泽东", "D":"江泽民"}, "answer": "A"}, #
    {"id": "03_s7", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 7, "question": "7. 中国共产党的性质决定了党的宗旨是（  ）。", "options": {"A":"立党为公、执政为民", "B":"以人为本、执政为民", "C":"全心全意为人民服务", "D":"为实现共产主义而奋斗"}, "answer": "C"}, #
    {"id": "03_s8", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 8, "question": "8.（  ）是我国的根本领导制度，居于统领地位。", "options": {"A":"党的组织原则", "B":"党的政治原则", "C":"党的领导制度", "D":"党的性质宗旨"}, "answer": "C"}, #
    {"id": "03_s9", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 9, "question": "9. 历史和现实证明，（   ）就没有中国特色社会主义的产生与发展。", "options": {"A":"没有中国共产党的指导", "B":"没有中国共产党的组织", "C":"没有中国共产党的领导", "D":"没有中国共产党的监督"}, "answer": "C"}, #
    {"id": "03_s10", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 10, "question": "10.（  ）将党的领导制度明确为我国根本领导制度。", "options": {"A":"党的十九大", "B":"党的十九届三中全会", "C":"党的十九届四中全会", "D":"党的十九届五中全会"}, "answer": "C"}, #
    {"id": "03_s11", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 11, "question": "11.《中国共产党党章》明确规定，中国共产党是中国工人阶级的先锋队，同时是（   ）。", "options": {"A":"中国人民的先锋队", "B":"中华民族的先锋队", "C":"中国人民和中华民族的先锋队", "D":"中国新阶层的先锋队"}, "answer": "C"}, #
    {"id": "03_s12", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 12, "question": "12. （   ）是中国特色社会主义最本质的特征。", "options": {"A":"以经济建设为中心", "B":"以人为本", "C":"“五位一体总体布局”", "D":"中国共产党的领导"}, "answer": "D"}, #
    {"id": "03_s13", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 13, "question": "13.面对新时代新挑战新要求，（  ）就是战胜艰难险阻，不断取得胜利的制胜法宝。", "options": {"A":"改进完善党的领导", "B":"坚持和加强党的领导", "C":"全面推进党的改革", "D":"增加党员人数"}, "answer": "B"}, #
    {"id": "03_s14", "type": "single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 14, "question": "14.中国共产党的领导是中国特色社会主义最本质的特征，这是（  ）以来习近平提出的一个重要论断。", "options": {"A":"党的十八大", "B":"党的十五大", "C":"党的十九大", "D":"党的十七大"}, "answer": "A"}, #
    # Multiple Choice (多项选择题) from 03.doc
    {"id": "03_m1", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 1, "question": "1.中国共产党领导是中国特色社会主义最本质的特征，（ ）。", "options": {"A":"这是在近代以来中国历史发展中形成的", "B":"这是由中国最广大人民根本利益决定的", "C":"这是实现中华民族伟大复兴历史任务决定的", "D":"这决定了中国特色社会主义其他特点和特征"}, "answer": "ABCD"}, #
    {"id": "03_m2", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 2, "question": "2.中国特色社会主义之所以是社会主义，究其根本就在于（  ）。", "options": {"A":"坚持科学社会主义基本原则", "B":"坚持中国共产党的领导", "C":"坚持按劳分配", "D":"坚持社会主义市场经济体制"}, "answer": "AB"}, #
    {"id": "03_m3", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 3, "question": "3.全面加强党的领导，（  ）。", "options": {"A":"使我们有效应对严峻复杂的国际形势和接踵而至的巨大风险挑战", "B":"有力推进了党和国家各项事业的顺利发展", "C":"胜利实现了全面建成小康社会的战略目标", "D":"开启了全面建设社会主义现代化国家新征程。", "E":"在反腐败、脱贫攻坚等重大斗争中，党的全面领导的优势得到充分彰显"}, "answer": "ABCDE"}, #
    {"id": "03_m4", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 4, "question": "4健全党的全面领导制度，必须（   ）。", "options": {"A":"必须完善党在各种组织中发挥领导作用的制度", "B":"必须完善党协调各方的机制", "C":"必须完善党领导各项事业的具体制度", "D":"必须完善人民代表大会制度"}, "answer": "ABC"}, #
    {"id": "03_m5", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 5, "question": "5.党的领导是做好党和国家各项工作的根本保证，是我国（  ）的根本点，绝对不能有丝毫动摇。", "options": {"A":"民族团结", "B":"社会稳定", "C":"政治稳定", "D":"经济发展"}, "answer": "ABCD"}, #
    {"id": "03_m6", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 6, "question": "6. 确保党始终总揽全局、协调各方，必须增强政治意识（  ），自觉维护党中央权威和集中统一领导，自觉在思想上政治上行动上同党中央保持高度一致。", "options": {"A":"大局意识", "B":"核心意识", "C":"中心意识", "D":"看齐意识"}, "answer": "ABD"}, #
    {"id": "03_m7", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 7, "question": "7. 党是最高政治领导力量，这是由我国（  ）和（ ）所决定的。", "options": {"A":"国家性质", "B":"国体政体", "C":"经济基础", "D":"经济制度"}, "answer": "AB"}, #
    {"id": "03_m8", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 8, "question": "8. 坚持和完善党的领导，是（  ）。", "options": {"A":"党和国家的根本所在、命脉所在", "B":"全国各族人民的利益所在、幸福所在", "C":"中国特色社会主义最本质的特征", "D":"中国特色社会主义制度的最大优势"}, "answer": "ABCD"}, #
    {"id": "03_m9", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 9, "question": "9.中国共产党是中国特色社会主义事业的（   ）。", "options": {"A":"开创者", "B":"推动者", "C":"引领者", "D":"发动者"}, "answer": "ABC"}, #
    {"id": "03_m10", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 10, "question": "10.党章规定的民主集中制要求（  ）。", "options": {"A":"党员个人服从党的组织", "B":"少数服从多数", "C":"下级组织服从上级组织", "D":"全党各个组织和全体党员服从党的全国代表大会和中央委员会"}, "answer": "ABCD"}, #
    {"id": "03_m11", "type": "multiple", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 11, "question": "11.坚持和加强党的全面领导，使党的（   ）显著增强.", "options": {"A":"政治领导力", "B":"思想引领力", "C":"群众组织力", "D":"社会号召力"}, "answer": "ABCD"}, #
    # Judgment (判断题) from 03.doc
    {"id": "03_j1", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 1, "question": "1.贯彻新发展理念，是新时代我国发展壮大的必由之路，全面从严治党是党永葆生机活力、走好新的赶考之路的必由之路。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "03_j2", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 2, "question": "2.坚持和完善党的领导，是党和国家的根本所在、命脉所在，是全国各族人民的利益所在、幸福所在。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "03_j3", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 3, "question": "3.党的全面领导既坚持党的集中统一领导原则，坚持党是最高政治领导力量，又坚持民主集中制、发扬党内民主，坚持党的领导与人民当家作主、依法治国有机统一。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "03_j4", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 4, "question": "4.党的领导是全面的，所以，党组织包揽包办一切事情。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, #
    {"id": "03_j5", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 5, "question": "5.加强和维护党中央权威和集中统一领导，是全党共同的政治责任，是党和国家事业发展的必然要求。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "03_j6", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 6, "question": "6.坚持党中央权威和集中统一领导，就可以不讲民主集中制。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, #
    {"id": "03_j7", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 7, "question": "7. 历史充分证明，没有中国共产党，就没有新中国，就没有中华民族伟大复兴，历史和人民选择了中国共产党。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "03_j8", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 8, "question": "8.把党的领导制度作为我国的根本领导制度，彰显了我们党的高度制度自觉、制度自信。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "03_j9", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 9, "question": "9.坚持党总揽全局、协调各方的领导核心地位，是党作为最高政治力量在治国理政中的必然要求。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "03_j10", "type": "judgment_as_single", "source_doc": "03.doc", "doc_order": 3, "q_num_in_doc": 10, "question": "10.中国共产党的自身优势是中国特色社会主义制度优势的主要来源。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #

    # --- Document 04.doc (doc_order: 4) ---
    # Single Choice (单项选择题)
    {"id": "04_s1", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 1, "question": "1.（  ）是立党为公、执政为民的本质要求。", "options": {"A":"贯彻新发展理念", "B":"实现高质量发展", "C":"为民造福", "D":"政治立场"}, "answer": "C"}, #
    {"id": "04_s2", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 2, "question": "2.（  ）始终是党的生命线和根本工作路线，是我们党永葆青春活力和战斗力的重要传家宝。", "options": {"A":"群众路线", "B":"经济路线", "C":"人民立场", "D":"政治立场"}, "answer": "A"}, #
    {"id": "04_s3", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 3, "question": "3.（  ）是新时代坚持和发展中国特色社会主义的根本立场，是贯穿党治国理政全部活动的一条红线。", "options": {"A":"把马克思主义基本原理与中国实际相结合", "B":"坚持以人民为中心", "C":"坚持和发展中国特色社会主义", "D":"“五位一体”总体布局"}, "answer": "B"}, #
    {"id": "04_s4", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 4, "question": "4.中国共产党区别于其他政党的显著标志是（  ）。", "options": {"A":"深化改革", "B":"人民立场", "C":"促进高质量发展", "D":"实事求是"}, "answer": "B"}, #
    {"id": "04_s5", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 5, "question": "5.（ ）是党执政的最大底气，也是党执政最深厚的根基。", "options": {"A":"实现共产主义理想", "B":"物质基础雄厚", "C":"有丰富经验", "D":"人民"}, "answer": "D"}, #
    {"id": "04_s6", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 6, "question": "6.（  ）是党的工作的最高裁决者和最终评判者。", "options": {"A":"实践", "B":"人民", "C":"国务院", "D":"党中央"}, "answer": "B"}, #
    {"id": "04_s7", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 7, "question": "7.（  ）是贯彻群众路线的有效途径。", "options": {"A":"以人民为中心", "B":"调查研究", "C":"把人民对美好生活作为奋斗目标", "D":"构建新发展格局"}, "answer": "B"}, #
    {"id": "04_s8", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 8, "question": "8.我们党讲宗旨，讲了很多话，但说到底还是（ ）这句话。", "options": {"A":"以人民为中心", "B":"为人民服务", "C":"坚持人民主体地位", "D":"群众路线是根本工作路线"}, "answer": "B"}, #
    {"id": "04_s9", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 9, "question": "9.新时代要坚持以人民为中心，在推动社会全面进步中促进（   ）的全面发展。", "options": {"A":"人", "B":"经济", "C":"政治", "D":"文化"}, "answer": "A"}, #
    {"id": "04_s10", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 10, "question": "10.（  ）是社会主义的本质要求，是中国式现代化的重要特征。", "options": {"A":"共同富裕", "B":"社会和谐", "C":"人民主体地位", "D":"解决社会主要矛盾"}, "answer": "A"}, #
    {"id": "04_s11", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 11, "question": "11.实现全体人民共同富裕的宏伟目标，最终靠的是（  ）。", "options": {"A":"人", "B":"奋斗", "C":"实干", "D":"发展"}, "answer": "D"}, #
    {"id": "04_s12", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 12, "question": "12.党执政后的最大危险是（  ）。", "options": {"A":"消极腐败", "B":"改革出问题", "C":"没有坚持公有制的主体地位", "D":"脱离群众"}, "answer": "D"}, #
    {"id": "04_s13", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 13, "question": "13.我们党的最大政治优势是（   ）。", "options": {"A":"党领导一切", "B":"走中国特色社会主义道路", "C":"人多力量大", "D":"密切联系群众"}, "answer": "D"}, #
    {"id": "04_s14", "type": "single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 14, "question": "14.邓小平指出：“社会主义最大的优越性就是（  ），这是体现社会主义本质的一个东西。”", "options": {"A":"党的领导", "B":"共同富裕", "C":"办事效率高", "D":"走和平发展道路"}, "answer": "B"}, #
    # Multiple Choice (多项选择题) from 04.doc
    {"id": "04_m1", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 1, "question": "1.对“江山就是人民、人民就是江山”的理解是（  ）。", "options": {"A":"闪耀着历史唯物主义的真理光芒", "B":"充分说明我国国体政体的人民性", "C":"人民是我们党的生命之根、执政之基、力量之源", "D":"这是由我们党的性质、宗旨决定的"}, "answer": "ABCD"}, #
    {"id": "04_m2", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 2, "question": "2.坚持人民立场，就要做到（   ）。", "options": {"A":"与人民风雨同舟、生死与共", "B":"始终牢记党的初心和使命", "C":"始终保持党同人民群众的血肉联系", "D":"坚持以人民为中心的执政理念"}, "answer": "ABCD"}, #
    {"id": "04_m3", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 3, "question": "3.党依靠人民创造历史伟业，就要做到（  ）。", "options": {"A":"尊重人民主体地位", "B":"尊重人民首创精神", "C":"激发人民群众的创新创造活力", "D":"总结、概括人民群众实践中形成的新鲜经验"}, "answer": "ABCD"}, #
    {"id": "04_m4", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 4, "question": "4.领导干部要树立这样的政绩观（  ）。", "options": {"A":"以人民满意不满意作为检验工作的最终评判标准", "B":"把为民办事、为民造福作为最重要的政绩", "C":"把为老百姓办了多少好事实事作为检验政绩的重要标准", "D":"以国内生产总值增长率论英雄", "E":"大搞劳民伤财的形象工程和政绩工程"}, "answer": "ABC"}, # # Corrected to ABC from ABCD as per source 21 (implied, no E) vs source 181 (ABCD)
    {"id": "04_m5", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 5, "question": "5.坚持以人民为中心的发展思想，要（  ）。", "options": {"A":"坚持和贯彻党的群众路线", "B":"把以人民为中心的发展思想切实贯穿到党和国家事业各方面", "C":"推动全体人民共同富裕取得更为明显的实质性进展。", "D":"总结、概括人民群众实践中形成的新鲜经验"}, "answer": "ABCD"}, #
    {"id": "04_m6", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 6, "question": "6.对党的群众路线的理解，（  ）。", "options": {"A":"其内容是一切为了群众，一切依靠群众，从群众中来，到群众中去", "B":"它是唯物史观关于人民群众是历史创造者的原理在党的工作中的运用", "C":"它充分体现了以人民为中心的根本政治立场", "D":"它是我们党永葆青春活力和战斗力的重要传家宝"}, "answer": "ABCD"}, #
    {"id": "04_m7", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 7, "question": "7.实现共同富裕 ，（  ）。", "options": {"A":"这是中国特色社会主义的本质要求", "B":"这是中国式现代化的重要特征", "C":"这不仅是经济问题，而且是关系党的执政基础的重大政治问题", "D":"这是解决我国发展不平衡不充分问题的现实需要", "E":"要处理好先富和共富的关系"}, "answer": "ABCDE"}, #
    {"id": "04_m8", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 8, "question": "8.扎实推进共同富裕，要把握好（  ）的原则。", "options": {"A":"鼓励勤劳创新致富", "B":"坚持基本经济制度", "C":"量力而行", "D":"坚持循序渐进", "E":"整齐划一"}, "answer": "ABCD"}, #
    {"id": "04_m9", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 9, "question": "9.党依靠人民，从小到大、从弱到强，打败了强大的内外敌人，取得了新民主主义革命胜利，实现了（   ），建立了中华人民共和国。", "options": {"A":"人民幸福", "B":"民族独立", "C":"人民解放", "D":"国家富强"}, "answer": "BC"}, #
    {"id": "04_m10", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 10, "question": "10.党依靠人民，推进（  ）走出一条中国特色社会主义道路。", "options": {"A":"改革开放", "B":"社会主义现代化建设", "C":"全面建成小康社会", "D":"社会主义现代化国家"}, "answer": "AB"}, #
    {"id": "04_m11", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 11, "question": "11.党依靠人民，推动党和国家事业（ ），推动中国特色社会主义进入新时代。", "options": {"A":"经济社会发展", "B":"人民生活更加富裕", "C":"发生历史性变革", "D":"取得历史性成就"}, "answer": "CD"}, #
    {"id": "04_m12", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 12, "question": "12.以人民为中心是我们党（  ）的生动体现，是全心全意为人民服务的时代彰显。", "options": {"A":"立党为公", "B":"落实群众路线", "C":"坚持宗旨原则", "D":"执政为民"}, "answer": "AD"}, #
    {"id": "04_m13", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 13, "question": "13. 以人民为中心的发展思想，不是高高在上的宣传口号，绝对不能只停留在口头上，要全方位贯穿于经济社会发展的各个环节，体现在人民群众（ ）的扎实提升上。", "options": {"A":"使命感", "B":"获得感", "C":"幸福感", "D":"安全感"}, "answer": "BCD"}, #
    {"id": "04_m14", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 14, "question": "14.（  ）与（  ）相统一，既是马克思主义的价值追求，也是社会主义的本质要求，更是中国共产党人的奋斗目标。", "options": {"A":"促进人的全面发展", "B":"促进社会稳定", "C":"促进共同富裕", "D":"促进经济发展"}, "answer": "AC"}, #
    {"id": "04_m15", "type": "multiple", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 15, "question": "15.坚持以人民为中心的发展思想，就要在高质量发展中促进共同富裕，做到（ ）", "options": {"A":"发展为了人民", "B":"发展幸福人民", "C":"发展依靠人民", "D":"发展成果由人民共享"}, "answer": "ACD"}, #
    # Judgment (判断题) from 04.doc
    {"id": "04_j1", "type": "judgment_as_single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 1, "question": "1.人民是历史的创造者，是决定党和国家前途命运的根本力量。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "04_j2", "type": "judgment_as_single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 2, "question": "2.组织路线始终是党的生命线和根本工作路线，是我们党永葆青春活力和战斗力的重要传家宝。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, #
    {"id": "04_j3", "type": "judgment_as_single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 3, "question": "3.中国共产党根基在人民、血脉在人民、力量在人民。人民是我们党的生命之根、执政之基、力量之源。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "04_j4", "type": "judgment_as_single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 4, "question": "4.“水能载舟、亦能覆舟”赢得人民信任、得到人民支持，党就能够克服任何困难。反之，我们将一事无成，甚至走向衰败。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "04_j5", "type": "judgment_as_single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 5, "question": "5.在中国共产党领导的社会主义中国，党性和人民性是一致的、统一的。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "04_j6", "type": "judgment_as_single", "source_doc": "04.doc", "doc_order": 4, "q_num_in_doc": 6, "question": "6.我们要实现14亿人共同富裕，必须脚踏实地、久久为功，不是所有人都同时富裕，也不是所有地区同时达到一个富裕水准，不可能齐头并进。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #

    # --- Document 05.doc (doc_order: 5) ---
    # Single Choice (单项选择题)
    {"id": "05_s1", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 1, "question": "1.习近平强调：“（  ）是决定当代中国命运的关键一招，也是决定实现’两个一百年’奋斗目标、实现中华民族伟大复兴的关键一招。”", "options": {"A":"高质量发展", "B":"改革开放", "C":"全面依法治国", "D":"文化自信"}, "answer": "B"}, #
    {"id": "05_s2", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 2, "question": "2.全面深化改革的总目标是（    ）。", "options": {"A":"推进国家治理体系和治理能力现代化", "B":"完善和发展中国特色社会主义制度，推进国家治理体系和治理能力现代化", "C":"进一步解放思想、发展社会生产力", "D":"赋予社会主义新的生机活力，推进国家治理体系和治理能力现代化"}, "answer": "B"}, #
    {"id": "05_s3", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 3, "question": "3.中国坚持对外开放的基本国策，坚定奉行（   ）的开放战略。", "options": {"A":"互利共赢", "B":"不结盟", "C":"“一带一路”倡议", "D":"构建人类命运共同体"}, "answer": "A"}, #
    {"id": "05_s4", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 4, "question": "4.“一带一路”建设，坚持（   ）原则，机会和成果属于全世界。", "options": {"A":"互利共赢", "B":"共商共建共享", "C":"共商共建", "D":"平等互惠"}, "answer": "B"}, #
    {"id": "05_s5", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 5, "question": "5.（  ）是新时代全面深化改革开放的思想前提。", "options": {"A":"实事求是", "B":"解放思想", "C":"开拓创新", "D":"贯彻新发展理念"}, "answer": "B"}, #
    {"id": "05_s6", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 6, "question": "6.党的十九大提出，到（  ）“各方面制度更加完善，国家治理体系和治理能力现代化基本实现”。", "options": {"A":"2035年", "B":"2030年", "C":"2025年", "D":"2020年"}, "answer": "A"}, #
    {"id": "05_s7", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 7, "question": "7.中国特色社会主义制度和国家治理体系是以（    ）为指导、植根中国大地、具有深厚中华文化根基、深得人民拥护的制度和治理体系。", "options": {"A":"社会主义", "B":"中国特色社会主义", "C":"马克思主义", "D":"毛泽东思想"}, "answer": "C"}, #
    {"id": "05_s8", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 8, "question": "8.坚持和完善中国特色社会主义制度、推进国家治理体系和治理能力现代化，不仅要建立完善的制度体系，还要在不断提高（  ）上狠下功夫。", "options": {"A":"民主与法治", "B":"制度创新和社会和谐", "C":"社会发展和经济增速", "D":"制度执行力和治理能力"}, "answer": "D"}, #
    {"id": "05_s9", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 9, "question": "9.（   ）作出了全面深化改革的决定。", "options": {"A":"党的十八大", "B":"党的十八届三中全会", "C":"党的十九大", "D":"党的十九届六中全会"}, "answer": "B"}, #
    {"id": "05_s10", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 10, "question": "10.全面深化改革能否顺利推进，关键取决于党，取决于（   ）。", "options": {"A":"全体人民的共同参与", "B":"党的集中统一领导", "C":"全方位对外开放", "D":"社会主义的发展方向"}, "answer": "B"}, #
    {"id": "05_s11", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 11, "question": "11.（    ）是运用国家制度管理国家各方面事务的能力。", "options": {"A":"治理能力", "B":"治理体系", "C":"管理能力", "D":"协调能力"}, "answer": "A"}, #
    {"id": "05_s12", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 12, "question": "12.（   ），习近平先后提出共建“丝绸之路经济带”和“21世纪海上丝绸之路”的重大倡议。", "options": {"A":"2015年9月和10月", "B":"2014年9月和10月", "C":"2013年9月和10月", "D":"2012年9月和10月"}, "answer": "C"}, #
    {"id": "05_s13", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 13, "question": "13.中阿新闻交流中心、中阿电子图书馆门户网站正式落地；“汉语热”在阿拉伯国家持续升温，沙特、阿联酋、埃及宣布将中文教学纳入国民教育体系。上述现象主要说明（  ）", "options": {"A":"各国之间经济互联互通", "B":"形成了“一带一路”产业化集群", "C":"“一带一路”促进人文交流更加深入", "D":"中华文化成为人类文明的中心"}, "answer": "C"}, #
    {"id": "05_s14", "type": "single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 14, "question": "14.推进改革的目的是要不断推进我国社会主义制度（   ），赋予社会主义新的生机活力。", "options": {"A":"自我完善和发展", "B":"现实性和实效性", "C":"人民性和整体性", "D":"整体推进和全面发展"}, "answer": "A"}, #
    # Multiple Choice (多项选择题) from 05.doc
    {"id": "05_m1", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 1, "question": "1.改革开放是（  ）。", "options": {"A":"决定当代中国命运的关键一招", "B":"坚持和发展中国特色社会主义的必由之路", "C":"党和人民大踏步赶上时代的重要法宝", "D":"完成新时代目标任务的必然要求"}, "answer": "ABCD"}, #
    {"id": "05_m2", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 2, "question": "2.改革开放是坚持和发展中国特色社会主义的必由之路，因为（   ）。", "options": {"A":"改革开放为中国特色社会主义开创、发展和完善提供了实践基础", "B":"改革开放深化了对社会主义建设规律的认识，为坚持和发展中国特色社会主义提供了有力支撑", "C":"谱写新时代中国特色社会主义的新篇章，依然需要全面深化改革、不断扩大对外开放", "D":"以上都正确"}, "answer": "ABCD"}, #
    {"id": "05_m3", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 3, "question": "3.党的十一届三中全会来，我国创造了（  ）两大奇迹,极大地改变了中国的面貌。", "options": {"A":"经济快速发展", "B":"社会长期稳定", "C":"民族团结", "D":"“新四大发明”"}, "answer": "AB"}, #
    {"id": "05_m4", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 4, "question": "4.当前，之所以要全面深化改革开放 ，是因为（   ）。", "options": {"A":"发展中不平衡、不协调、不可持续问题依然突出", "B":"科技创新能力不强", "C":"产业结构不合理，发展方式依然粗放", "D":"城乡区域发展差距和居民收入分配差距依然较大", "E":"形式主义、官僚主义、享乐主义和奢靡之风问题突出"}, "answer": "ABCDE"}, #
    {"id": "05_m5", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 5, "question": "5.全面深化改革开放，必须（    ）。", "options": {"A":"勇于破除一切不合时宜的观念，深入贯彻新理念新思想新战略", "B":"勇于打破部门利益、行业利益、本位思想，服从国家整体利益", "C":"勇于破除根本制度、基本制度障碍，构建系统完备、科学规范、运行有效的制度体系", "D":"勇于破解我国开放型经济体制建设中的突出问题，积极适应经济全球化新趋势。"}, "answer": "ABD"}, #
    {"id": "05_m6", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 6, "question": "6.全面深化改革开放，是一场全面、系统、整体的制度创新，要着眼于建立一整套更完备、更稳定、更管用的制度体系，包括（    ）。", "options": {"A":"坚持和完善人民当家作主制度体系", "B":"完善涉外经济法律和规则体系", "C":"坚持和完善繁荣发展社会主义先进文化的制度", "D":"坚持和完善统筹城乡的民生保障制度和共建共治共享的社会治理制度", "E":"坚持和完善生态文明制度体系"}, "answer": "ABCDE"}, #
    {"id": "05_m7", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 7, "question": "7.改革开放要坚守政治原则和底线，不是改弦易张。这里面最核心的是（  ）、（ ），偏离了这一条，那就南辕北辙了。", "options": {"A":"坚持和改善人民代表大会制度", "B":"坚持和改善党的领导", "C":"坚持和完善中国特色社会主义制度", "D":"建成社会主义现代化国家"}, "answer": "BC"}, #
    {"id": "05_m8", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 8, "question": "8.改革开放是有方向、有立场、有原则的，必须（    ）。", "options": {"A":"有利于进一步解放思想、进一步解放和发展社会生产力", "B":"坚持以人民为中心，促进社会公平正义、增进人民福祉", "C":"坚持和改善党的全面领导、坚持和完善中国特色社会主义制度", "D":"推进我国社会主义制度自我完善和发展，赋予社会主义新的生机活力"}, "answer": "ABCD"}, #
    {"id": "05_m9", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 9, "question": "9.推进国家治理体系和治理能力现代化，（  ）。", "options": {"A":"这是一个国家现代化的重要标志", "B":"必须坚定中国特色社会主义制度自信", "C":"必须更好发挥中国特色社会主义制度优势", "D":"必须把中国特色社会主义制度优势转化为国家治理效能"}, "answer": "ABCD"}, #
    {"id": "05_m10", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 10, "question": "10.下面哪些是全面深化改革开放必须坚持的正确方法。（   ）", "options": {"A":"增强全面深化改革的系统性、整体性、协同性", "B":"加强顶层设计和摸着石头过河相结合", "C":"统筹改革发展稳定", "D":"胆子要大，步子要稳", "E":"凡属重大改革都要于法有据"}, "answer": "ABCDE"}, #
    {"id": "05_m11", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 11, "question": "11改革开放只有进行时、没有完成时，因为（   ）。", "options": {"A":"这是社会基本矛盾运动规律的深刻反映", "B":"这是总结世界社会主义实践经验得出的重要结论", "C":"这是推进党和人民事业发展的必然要求", "D":"全面建设社会主义现代化国家新，根本动力仍然是改革开放。"}, "answer": "ABCD"}, #
    {"id": "05_m12", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 12, "question": "12.全面深化改革要在哪些领域发力。（  ）", "options": {"A":"要深化社会主义市场经济体制改革", "B":"深化人民当家作主制度体系改革", "C":"深化文化体制改革", "D":"健全加强党的全面领导、全面从严治党制度", "E":"深化社会体制改革"}, "answer": "ABCDE"}, #
    {"id": "05_m13", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 13, "question": "13.对外开放面临的新形势是（   ）。", "options": {"A":"当今世界正在经历百年未有之大变局，新一轮科技革命和产业变革深入发展", "B":"逆全球化思潮抬头，单边主义、保护主义明显上升", "C":"局部冲突和动荡频发，全球性问题加剧", "D":"我国经济发展进入新常态，资源约束日益趋紧，环境承载能力接近上限", "E":"我国人力资源丰富，市场规模庞大，基础设施比较完善、产业配套齐全"}, "answer": "ABCDE"}, #
    {"id": "05_m14", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 14, "question": "14.党的十八大以来，我国全面开放新举措是（  ）。", "options": {"A":"推进“一带一路”建设", "B":"推进贸易强国建设", "C":"积极营造国际一流营商环境", "D":"优化区域开放布局", "E":"统筹多双边和区域开放合作"}, "answer": "ABCDE"}, #
    {"id": "05_m15", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 15, "question": "15.构建更高水平开放型经济新体制，必须（   ）。", "options": {"A":"依托我国超大规模市场优势，以国内大循环吸引全球资源要素，提升贸易投资合作质量和水平。", "B":"深化贸易投资领域体制机制改革，稳步扩大规则、规制、管理、标准等制度型开放。", "C":"推动货物贸易优化升级，创新服务贸易发展机制，发展数字贸易，加快建设贸易强国。", "D":"推动共建“一带一路”高质量发展。", "E":"优化区域开放布局，实施自由贸易试验区提升战略，"}, "answer": "ABCDE"}, #
    {"id": "05_m16", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 16, "question": "16.在全面深化改革中，要增强改革的（    ）。", "options": {"A":"系统性", "B":"整体性", "C":"协同性", "D":"同一性"}, "answer": "ABC"}, #
    {"id": "05_m17", "type": "multiple", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 17, "question": "17.全面深化改革的总目标是（    ）。", "options": {"A":"实现两个百年目标", "B":"实现中国梦", "C":"完善和发展中国特色社会主义制度", "D":"推进国家治理体系和治理能力现代化"}, "answer": "CD"}, #
    # Judgment (判断题) from 05.doc
    {"id": "05_j1", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 1, "question": "1.新时代全面深化改革开放，就其艰巨性、复杂性和系统性来说，是一场深刻的革命。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "05_j2", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 2, "question": "2.改革是由问题倒逼而产生，改革进程中的矛盾只能用改革的办法来解决。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "05_j3", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 3, "question": "3.凡属重大改革不必于法有据，需要修改法律的可以不用先修改法律，先破后立。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, #
    {"id": "05_j4", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 4, "question": "4.中国对外开放，不是要一家唱独角戏，而是要欢迎各方共同参与；不是要谋求势力范围，而是要支持各国共同发展；不是要营造自己的后花园，而是要建设各国共享的百花园。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "05_j5", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 5, "question": "5.我国国家制度和国家治理体系的显著优势，要坚持以人民为中心的发展思想，不断保障和改善民生、增进人民福祉，走共同富裕道路的显著优势。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "05_j6", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 6, "question": "6.我国构建互利共赢、多元平衡、安全高效的开放型经济体系，不断增强我国国际经济合作和竞争新优势。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "05_j7", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 7, "question": "7.党的十一届三中全会是划时代的，开启了改革开放和社会主义现代化建设新时期。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "05_j8", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 8, "question": "8.党的二十大指出，要推进高水平对外开放，稳步扩大规则、规制、管理、标准等制度型开放。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, #
    {"id": "05_j9", "type": "judgment_as_single", "source_doc": "05.doc", "doc_order": 5, "q_num_in_doc": 9, "question": "10.党的二十大指出，全面建设社会主义现代化国家的前进道路上，要牢牢把握五项重大原则：坚持和加强的全面领导，坚持中国特色社会主义道路、坚持以人民为中心的发展思想、坚持深化改革开放和坚持发扬斗争精神。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # # Source has q number 10, I assigned 9 based on sequence.
    
    # --- Document 06.doc (doc_order: 6) ---
    # Single Choice (单项选择题)
    {"id": "06_s1", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 1, "question": "1.（  ）是实现高质量发展的指导原则。", "options": {"A":"新发展阶段", "B":"新发展方位", "C":"新发展理念", "D":"供给侧改革"}, "answer": "C"}, # [cite: 1]
    {"id": "06_s2", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 2, "question": "2. 党的十八大以来，我国经济已由高速增长阶段转向（）阶段。", "options": {"A":"世界级市场", "B":"高水平开放", "C":"强动力转换", "D":"高质量发展"}, "answer": "D"}, # [cite: 1]
    {"id": "06_s3", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 3, "question": "3.（）是引领发展的第一动力。", "options": {"A":"劳动力", "B":"资本", "C":"科技", "D":"创新"}, "answer": "D"}, # [cite: 1]
    {"id": "06_s4", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 4, "question": "4.构建高水平社会主义市场经济体制，关键是要（ ）。", "options": {"A":"处理好政府和市场的关系", "B":"处理好当前利益和长远利益的关系", "C":"处理好中国和外国的关系", "D":"处理好效率和公平的关系"}, "answer": "A"}, # [cite: 1]
    {"id": "06_s5", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 5, "question": "5.我们乘势而上开启全面建设社会主义现代化国家新征程、向第二个百年奋斗目标进军，这标志着我国进入了一个（  ）。", "options": {"A":"新发展时期", "B":"新发展方位", "C":"新发展阶段", "D":"新发展格局"}, "answer": "C"}, # [cite: 1]
    {"id": "06_s6", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 6, "question": "6.（  ）是发展行动的先导。", "options": {"A":"发展理念", "B":"发展格局", "C":"发展方向", "D":"发展策略"}, "answer": "A"}, # [cite: 1]
    {"id": "06_s7", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 7, "question": "7.（  ）的发展理念，相互贯通、相互促进，是具有内在联系的集合体，要统一贯彻，不能顾此失彼，也不能相互替代。", "options": {"A":"改革、和谐、绿色、开放、共享", "B":"创新、协调、和谐、开放、共赢", "C":"创新、和谐、绿色、开放、发展", "D":"创新、协调、绿色、开放、共享"}, "answer": "D"}, # [cite: 1]
    {"id": "06_s8", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 8, "question": "8.（  ）是根据我国发展阶段、环境、条件变化提出来的，是重塑我国国际合作和竞争新优势的战略抉择。", "options": {"A":"新发展理念", "B":"新发展格局", "C":"新发展阶段", "D":"新发展时期"}, "answer": "B"}, # [cite: 1]
    {"id": "06_s9", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 9, "question": "9.现代化经济体系必须坚持质量第一、（   ）优先。", "options": {"A":"利益", "B":"速度", "C":"人才", "D":"效益"}, "answer": "D"}, # [cite: 2]
    {"id": "06_s10", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 10, "question": "10.（ ）是化解我国经济发展面临困难和矛盾的重大举措。", "options": {"A":"供给侧结构性改革", "B":"健全民主法制", "C":"社会公平正义", "D":"人民主体地位"}, "answer": "A"}, # [cite: 2]
    {"id": "06_s11", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 11, "question": "11.建设充分发挥（   ），更好发挥政府作用的经济体制。", "options": {"A":"市场作用", "B":"服务业动能", "C":"社会作用", "D":"社会福利补给"}, "answer": "A"}, # [cite: 2]
    {"id": "06_s12", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 12, "question": "12.经济改革的方向是要让（  ）在资源配置中发挥决定性作用。", "options": {"A":"科技", "B":"创新", "C":"政府", "D":"市场"}, "answer": "D"}, # [cite: 2]
    {"id": "06_s13", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 13, "question": "13.我国经济已由高速增长阶段转向（ ），正处在转变发展方式、优化经济结构、转换增长动力的攻关期。", "options": {"A":"高质量发展阶段", "B":"中高速阶段", "C":"低速阶段", "D":"高水平发展阶段"}, "answer": "A"}, # [cite: 2]
    {"id": "06_s14", "type": "single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 14, "question": "14.国有企业是中国特色社会主义的重要物质基础和政治基础，关系（  ）地位的巩固，关系我们党的执政地位和执政能力，关系我国社会主义制度。", "options": {"A":"人民主体", "B":"公有制主体", "C":"经济体制主体", "D":"社会发展主体"}, "answer": "B"}, # [cite: 2]
    # Multiple Choice (多项选择题) from 06.doc
    {"id": "06_m1", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 1, "question": "1.新发展阶段是（ ）。", "options": {"A":"我国社会主义初级阶段历史进程中的一个重要阶段", "B":"中国共产党带领人民迎来从站起来、富起来到强起来历史性跨越的新阶段", "C":"全面建设社会主义现代化国家、向第二个百年奋斗目标进军的重要阶段。", "D":"决胜全面小康社会的阶段"}, "answer": "ABCD"}, # [cite: 2]
    {"id": "06_m2", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 2, "question": "2.全面地理解和把握新发展理念，（  ）", "options": {"A":"要从根本宗旨上把握新发展理念，坚持以人民为中心的发展思想", "B":"要从问题导向上把握新发展理念，切实解决发展不平衡不充分问题", "C":"要从忧患意识上把握新发展理念，下好先手棋，打好主动仗", "D":"新发展理念是引领我国发展全局深刻变革的科学指引"}, "answer": "ABCD"}, # [cite: 2, 3]
    {"id": "06_m3", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 3, "question": "3.新发展理念具有丰富的科学内涵和具体的实践要求是（ ）。", "options": {"A":"创新是引领发展的第一动力，创新发展注重的是解决发展动力问题", "B":"协调是持续健康发展的内在要求，协调发展注重的是解决发展不平衡问题", "C":"绿色是永续发展的必要条件和人民对美好生活追求的重要体现，绿色发展注重的是解决人与自然和谐共生问题", "D":"开放是国家繁荣发展的必由之路，开放发展注重的是解决发展内外联动问题", "E":"共享是中国特色社会主义的本质要求，共享发展注重的是解决社会公平正义问题"}, "answer": "ABCDE"}, # [cite: 3]
    {"id": "06_m4", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 4, "question": "4.高质量发展的重大战略意义是（  ）。", "options": {"A":"高质量发展为全面建设社会主义现代化国家提供更为坚实的物质基础。", "B":"高质量发展是不断满足人民对美好生活需要的重要保证。", "C":"高质量发展是维护国家长治久安的必然要求。", "D":"以上都对"}, "answer": "ABCD"}, # [cite: 3, 4]
    {"id": "06_m5", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 5, "question": "5.公有制经济包括（  ）。", "options": {"A":"国有经济", "B":"集体经济", "C":"混合所有制经济中的国有成分", "D":"混合所有制经济中的集体成分"}, "answer": "ABCD"}, # [cite: 4]
    {"id": "06_m6", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 6, "question": "6.公有制经济 (   )。", "options": {"A":"是全体人民的宝贵财富", "B":"是我国各族人民共享发展成果的制度性保证", "C":"是巩固党的执政地位、坚持我国社会主义制度的重要保证", "D":"公有制主体地位不能动摇"}, "answer": "ABCD"}, # [cite: 4]
    {"id": "06_m7", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 7, "question": "7.以下对于国有企业认识的观点，正确的是（  ）。", "options": {"A":"国有企业是中国特色社会主义的重要物质基础和政治基础", "B":"国有企业与民争利", "C":"要深化国有企业改革,坚持有利于国有资产保值增值", "D":"推动国有资本和国有企业做强做优做大。", "E":"坚持党对国有企业的领导不动摇"}, "answer": "ACDE"}, # [cite: 4]
    {"id": "06_m8", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 8, "question": "8.非公有制经济包括（  ）。", "options": {"A":"个体经济", "B":"民营经济", "C":"港澳台投资经济", "D":"外商投资经济", "E":"混合所有制经济中的非国有成分和非集体成分"}, "answer": "ABCDE"}, # [cite: 4, 5]
    {"id": "06_m9", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 9, "question": "9.我国非公有制经济是(  )。", "options": {"A":"社会主义市场经济的重要组成部分", "B":"稳定经济的重要基础", "C":"国家税收的重要来源", "D":"就业创业的重要领域，", "E":"经济持续健康发展的重要力量"}, "answer": "ABCDE"}, # [cite: 5]
    {"id": "06_m10", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 10, "question": "10.构建新发展格局是（  ）。", "options": {"A":"把握未来发展主动权的先手棋", "B":"开放的国内国际双循环，不是封闭的国内单循环", "C":"以全国统一大市场基础上的国内大循环为主体,不是各地都搞自我小循环", "D":"事关全局的系统性、深层次变革", "E":"适应我国发展新阶段要求、塑造国际合作和竞争新优势的必然选择"}, "answer": "ABCDE"}, # [cite: 5]
    {"id": "06_m11", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 11, "question": "11.构建新发展格局，必须（   ）。", "options": {"A":"具备强大的国内经济循环体系和稳固的基本盘，巩固和发展我国经济的强大竞争力", "B":"发挥比较优势，以国内大循环吸引全球资源要素", "C":"保证经济循环的畅通无阻", "D":"实现经济在高水平上的动态平衡"}, "answer": "ABCD"}, # [cite: 5]
    {"id": "06_m12", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 12, "question": "12.大力推动构建新发展格局，必须（   ）。", "options": {"A":"坚持持问题导向和系统观念", "B":"着力破除制约加快构建新发展格局的主要矛盾和问题", "C":"着力发展实体经济", "D":"着力推动实施扩大内需战略同深化供给侧结构性改革有机结合", "E":"着力推动产业链供应链优化升级"}, "answer": "ABCDE"}, # [cite: 5]
    {"id": "06_m13", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 13, "question": "13.建设现代化产业体系", "options": {"A":"巩固优势产业领先地位", "B":"大力发展战略性新兴产业", "C":"构建优质高效的服务业新体系", "D":"发展现代流通产业", "E":"加快发展数字经济"}, "answer": "ABCDE"}, # [cite: 5]
    {"id": "06_m14", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 14, "question": "14.促进区域协调发展，（  ）。", "options": {"A":"是贯彻新发展理念的重要内容，也是实现高质量发展的必然要求", "B":"要深入实施区域协调发展战略、区域重大战略、主体功能区战略", "C":"要推进以人为核心的新型城镇化，加快农业转移人口市民化。", "D":"要求各地区在经济发展上达到同一水平"}, "answer": "ABC"}, # [cite: 5]
    {"id": "06_m15", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 15, "question": "15.建设（  ）的高标准市场体系，是发挥我国市场优势的必然选择。", "options": {"A":"统一开放", "B":"竞争有序", "C":"制度完备", "D":"治理完善"}, "answer": "ABCD"}, # [cite: 5]
    {"id": "06_m16", "type": "multiple", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 16, "question": "16.社会主义基本经济制度包括（  ）。", "options": {"A":"公有制为主体、多种所有制经济共同发展", "B":"按劳分配为主体、多种分配方式并存", "C":"社会主义市场经济体制", "D":"人民代表大会制度"}, "answer": "ABC"}, # [cite: 5]
    # Judgment (判断题) from 06.doc
    {"id": "06_j1", "type": "judgment_as_single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 1, "question": "1．坚持创新发展、协调发展、绿色发展、开放发展、共享发展，是关系我国发展全局的一场深刻变革。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 6]
    {"id": "06_j2", "type": "judgment_as_single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 2, "question": "2.共享既是发展手段又是发展目标，同时还是评价发展的标准和尺度。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 6]
    {"id": "06_j3", "type": "judgment_as_single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 3, "question": "3.经济发展是一个螺旋式上升的过程，上升不是线性的，量积累到一定阶段，必须转向质的提升，我国经济发展也要遵循这一规律。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 6]
    {"id": "06_j4", "type": "judgment_as_single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 4, "question": "4.我国将立足新发展阶段，贯穿新发展理念，积极构建以国际大循环为主体、国内国际双循环相互促进的新发展格局。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 6]
    {"id": "06_j5", "type": "judgment_as_single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 5, "question": "5．建设现代化经济体系是我国发展的战略目标，是推动高质量发展、全面提高经济整体竞争力的必然要求。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 6]
    {"id": "06_j6", "type": "judgment_as_single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 6, "question": "6．全面建设社会主义现代化国家，最艰巨最繁重的任务依然在农村，最广泛最深厚的基础依然在农村。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 6]
    {"id": "06_j7", "type": "judgment_as_single", "source_doc": "06.doc", "doc_order": 6, "q_num_in_doc": 7, "question": "7．坚持全民共享、全面共享、共建共享、渐进共享，使全体人民有更多获得感、幸福感、安全感，朝着共同富裕方向稳步前进。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 6]

    # --- Document 07.doc (doc_order: 7) ---
    # Single Choice (单项选择题)
    {"id": "07_s1", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 1, "question": "1. 必须坚持(   )是第一生产力。", "options": {"A":"人才", "B":"资源", "C":"科技", "D":"环境"}, "answer": "C"}, # [cite: 7]
    {"id": "07_s2", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 2, "question": "2.（ ）是发展第一动力。", "options": {"A":"科技", "B":"人才", "C":"创新", "D":"党的领导"}, "answer": "C"}, # [cite: 7]
    {"id": "07_s3", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 3, "question": "3.（ ）提出“科学技术是第一生产力”。", "options": {"A":"毛泽东", "B":"邓小平", "C":"习近平", "D":"胡锦涛"}, "answer": "B"}, # [cite: 7]
    {"id": "07_s4", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 4, "question": "4.科教兴国是我国的（  ）。", "options": {"A":"基本国策", "B":"基本政策", "C":"基本路线", "D":"基本战略"}, "answer": "A"}, # [cite: 7]
    {"id": "07_s5", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 5, "question": "5.（  ）是民族振兴、社会进步的基石。", "options": {"A":"科技", "B":"教育", "C":"共同富裕", "D":"人才"}, "answer": "B"}, # [cite: 7, 8]
    {"id": "07_s6", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 6, "question": "6.（   ）是发展教育的根本尺度。", "options": {"A":"科技突破", "B":"人民满意", "C":"实现共同富裕", "D":"发展生产力"}, "answer": "B"}, # [cite: 8]
    {"id": "07_s7", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 7, "question": "7.（  ）是国家强盛之基、安全之要。", "options": {"A":"科技自立自强", "B":"人才引进", "C":"共同富裕", "D":"改革开放"}, "answer": "A"}, # [cite: 8]
    {"id": "07_s8", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 8, "question": "8.（  ）是我们攀登世界科技高峰的必由之路。", "options": {"A":"自主创新", "B":"脱贫攻坚", "C":"守正创新", "D":"信息技术"}, "answer": "A"}, # [cite: 8]
    {"id": "07_s9", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 9, "question": "9.必须坚持教育优先发展，把（  ）作为教育的根本任务，办好人民满意的教育。", "options": {"A":"立德树人", "B":"社会实践", "C":"创新拔尖", "D":"专业技术"}, "answer": "A"}, # [cite: 8]
    {"id": "07_s10", "type": "single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 10, "question": "10.（  ）是科技创新的源头。我国面临的很多“卡脖子”技术问题，根子是基础理论研究跟不上。", "options": {"A":"应用研究", "B":"国家实验室", "C":"经济特区", "D":"基础研究"}, "answer": "D"}, # [cite: 8]
    # Multiple Choice (多项选择题) from 07.doc
    {"id": "07_m1", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 1, "question": "1.全面建设社会主义现代化国家,(   )。", "options": {"A":"教育是根本", "B":"科技是关键", "C":"人才是基础", "D":"改革是保证"}, "answer": "ABC"}, # [cite: 8, 9]
    {"id": "07_m2", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 2, "question": "2. 实施（  ）是增强综合国力、满足人民群众美好生活需要的必然要求，是建设教育强国、科技强国、人才强国的重大举措", "options": {"A":"科教兴国战略", "B":"人才强国战略", "C":"创新驱动发展战略", "D":"“四个全面战略”"}, "answer": "ABC"}, # [cite: 9]
    {"id": "07_m3", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 3, "question": "3.实施科教兴国战略，（   ）。", "options": {"A":"是应对新时代环境变化的必然要求", "B":"是建设创新型国家的必然要求", "C":"是应对国际竞争的有力举措", "D":"是决胜全面小康社会的重大部署"}, "answer": "ABC"}, # [cite: 9]
    {"id": "07_m4", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 4, "question": "4.实施人才强国战略，（  ），实施更加积极、更加开放、更加有效的人才政策。", "options": {"A":"要坚持党管人才原则", "B":"坚持尊重劳动、尊重知识、尊重人才、尊重创造", "C":"完善人才战略布局", "D":"深化人才发展体制机制改革"}, "answer": "ABCD"}, # [cite: 9]
    {"id": "07_m5", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 5, "question": "5.实施创新驱动发展战略，（   ），让创新成为全社会的共同行动。", "options": {"A":"要坚持面向世界科技前沿、面向经济主战场", "B":"要坚持面向国家重大需求、面向人民生命健康", "C":"坚持科技创新，增强自主创新能力", "D":"坚决打赢关键核心技术攻坚战"}, "answer": "ABCD"}, # [cite: 9]
    {"id": "07_m6", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 6, "question": "6. 教育优先发展，要做到（  ），使我国教育越办越好。", "options": {"A":"经济社会发展规划优先安排教育发展", "B":"财政资金投入优先保障教育投入", "C":"公共资源配置优先满足教育和人力资源开发需要", "D":"推动健全优先发展教育事业的体制机制"}, "answer": "ABCD"}, # [cite: 9, 10]
    {"id": "07_m7", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 7, "question": "7. 建设教育强国是（   ）。", "options": {"A":"全面建成社会主义现代化强国的战略先导", "B":"是实现高水平科技自立自强的重要支撑", "C":"是以中国式现代化全面推进中华民族伟大复兴的基础工程,", "D":"必须把教育事业放在优先发展的战略位置"}, "answer": "ABCD"}, # [cite: 10]
    {"id": "07_m8", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 8, "question": "8.必须坚持教育（    ）。", "options": {"A":"为人民服务", "B":"为中国共产党治国理政服务", "C":"为巩固和发展中国特色社会主义制度服务", "D":"为改革开放和社会主义现代化建设服务"}, "answer": "ABCD"}, # [cite: 10]
    {"id": "07_m9", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 9, "question": "9.落实立德树人根本任务，必须着力解决好（  ）的问题，这是教育的根本问题，也是（  ）的核心课题。", "options": {"A":"培养什么人", "B":"怎样培养人", "C":"为谁培养人", "D":"建设教育强国"}, "answer": "ABC"}, # [cite: 10] # D is not part of the typical "three questions" for education's fundamental task.
    {"id": "07_m10", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 10, "question": "10.我们培养的人，（   ）。", "options": {"A":"要坚定共产主义远大理想和中国特色社会主义共同理想", "B":"要有高尚的道德品质，厚植爱国主义情怀", "C":"要养成刻苦学习的习惯", "D":"要积极投身社会实践，增长经验和技能"}, "answer": "ABCD"}, # [cite: 10]
    {"id": "07_m11", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 11, "question": "11.办好人民满意的教育，（ ）。", "options": {"A":"大力促进教育公平", "B":"加快建设高质量教育体系", "C":"提升教育服务经济社会发展能力", "D":"坚持深化教育改革创新", "E":"坚持把教师队伍建设作为基础工作"}, "answer": "ABCDE"}, # [cite: 10]
    {"id": "07_m12", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 12, "question": "12.实现高水平科技自立自强是（    ）。", "options": {"A":"应对风险挑战和维护国家利益的必然选择", "B":"构建新发展格局的内在要求", "C":"推动高质量发展的内在要求", "D":"满足人民美好生活需要的内在要求"}, "answer": "ABCD"}, # [cite: 10]
    {"id": "07_m13", "type": "multiple", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 13, "question": "13.建设人才强国，必须（   ）。", "options": {"A":"走好人才自主培养之路", "B":"加快建设世界重要人才中心和创新高地", "C":"坚持党对人才工作的全面领导", "D":"深化人才发展体制机制改革", "E":"营造识才爱才敬才用才的环境"}, "answer": "ABCDE"}, # [cite: 10]
    # Judgment (判断题) from 07.doc
    {"id": "07_j1", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 1, "question": "1.实现高水平科技自立自强是国家强盛和民族复兴的战略基石。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 10]
    {"id": "07_j2", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 2, "question": "2.全面建成社会主义现代化强国关键看科技自立自强。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 10]
    {"id": "07_j3", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 3, "question": "3.科技创新是百年未有之大变局中的一个关键变量，世界主要国家纷纷把科技创新作为国际战略博弈的主要战场。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 10]
    {"id": "07_j4", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 4, "question": "4.把教育技术掌握在自己手中，才能真正掌握竞争和发展的主动权。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 10] # Usually "关键核心技术"
    {"id": "07_j5", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 5, "question": "5.培养入才是国家和民族长远发展大计。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 10] # "入才" should be "人才"
    {"id": "07_j6", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 6, "question": "6.坚持党对人才工作的全面领导,这是做好人才工作的根本保证.", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 10, 11]
    {"id": "07_j7", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 7, "question": "7.科技是富国之本、兴邦大计。科技已经成为推动社会发展最活跃、最积极的因素。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 11] # "创新是引领发展的第一动力" is more common.
    {"id": "07_j8", "type": "judgment_as_single", "source_doc": "07.doc", "doc_order": 7, "q_num_in_doc": 8, "question": "8.人才是国之大计、党之大计，是国家经济社会发展的支撑力量，在国家发展中始终具有基础性先导性全局性地位。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 11] # "教育是国之大计、党之大计"

    # --- Document 08.doc (doc_order: 8) ---
    # Single Choice (单项选择题)
    {"id": "08_s1", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 1, "question": "1.我国是工人阶级领导的、以工农联盟为基础的(  )的社会主义国家，国家一切权力属于人民。", "options": {"A":"人民民主专政", "B":"人民当家作主", "C":"中国共产党领导", "D":"民主专政"}, "answer": "A"}, # [cite: 12]
    {"id": "08_s2", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 2, "question": "2.(  )是人民当家作主和依法治国的根本保证。", "options": {"A":"人民民主", "B":"党的领导", "C":"宪法", "D":"全过程民主"}, "answer": "B"}, # [cite: 12]
    {"id": "08_s3", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 3, "question": "3.人民当家作主是社会主义民主政治的本质特征，(    )是党领导人民治理国家的基本方式.", "options": {"A":"依法治国", "B":"坚持系统观念", "C":"全过程民主", "D":"民主集中制"}, "answer": "A"}, # [cite: 12, 13]
    {"id": "08_s4", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 4, "question": "4.（  ）是党克敌制胜、执政兴国的重要法宝，是团结海内外全体中华儿女实现中华民族伟大复兴的重要法宝。", "options": {"A":"协商民主", "B":"统一战线", "C":"全过程人民民主", "D":"实现中华民族伟大复兴"}, "answer": "B"}, # [cite: 13]
    {"id": "08_s5", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 5, "question": "5.（   ）是统一战线最核心、最根本的问题。", "options": {"A":"大团结大联合", "B":"广交朋友", "C":"凝聚人心", "D":"坚持党的领导"}, "answer": "D"}, # [cite: 13]
    {"id": "08_s6", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 6, "question": "6.统战工作的关键是要(   )。", "options": {"A":"坚持求同存异", "B":"坚持党的领导", "C":"坚持同一性", "D":"坚持多样性"}, "answer": "A"}, # [cite: 13]
    {"id": "08_s7", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 7, "question": "7.社会主义民主的实质是（   ）。", "options": {"A":"民主集中制", "B":"人民当家作主", "C":"人民代表大会制度", "D":"中华民族大团结"}, "answer": "B"}, # [cite: 13]
    {"id": "08_s8", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 8, "question": "8.一个国家是不是民主，应该由这个国家的（   ）来评判，而不应该由外部少数人指手画脚来评判。", "options": {"A":"人民", "B":"执政党", "C":"社会团体", "D":"国家性质"}, "answer": "A"}, # [cite: 13, 14]
    {"id": "08_s9", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 9, "question": "9.（   ）是社会主义的生命，没有民主就没有社会主义。", "options": {"A":"人民民主", "B":"人民当家作主", "C":"以人民为中心", "D":"坚持人民的主体地位"}, "answer": "A"}, # [cite: 14]
    {"id": "08_s10", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 10, "question": "10.（   ）是中国发展全过程人民民主的根本保证。", "options": {"A":"人民当家作主", "B":"中国特色社会主义制度", "C":"人民民主专政", "D":"中国共产党的领导"}, "answer": "D"}, # [cite: 14]
    {"id": "08_s11", "type": "single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 11, "question": "11.（  ）是指民主的制度安排，实质民主是指民主始终追求的价值目标，二者有机结合。", "options": {"A":"程序民主", "B":"协商民主", "C":"人民民主", "D":"全过程人民民主"}, "answer": "A"}, # [cite: 14]
    # Multiple Choice (多项选择题) from 08.doc
    {"id": "08_m1", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 1, "question": "1.人民民主是社会主义的生命，没有民主（  ）。", "options": {"A":"就没有社会主义", "B":"就没有社会主义的现代化", "C":"就没有中华民族伟大复兴", "D":"以上都对"}, "answer": "ABCD"}, # [cite: 14]
    {"id": "08_m2", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 2, "question": "2.（   ）构成我国的基本政治制度。", "options": {"A":"中国共产党领导的多党合作和政治协商制度", "B":"民族区域自治制度", "C":"基层群众自治制度", "D":"人民代表大会制度"}, "answer": "ABC"}, # [cite: 14, 15]
    {"id": "08_m3", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 3, "question": "3.屮国特色社会主义政治制度（  ）。", "options": {"A":"既把握了长期形成的历史传承，又把握了走过的发展道路", "B":"把握了现实要求、着眼解决现实问题", "C":"注重历史和现实、理论和实践、形式和内容有机统一", "D":"具有鲜明的中国特色、民族特色、时代特色"}, "answer": "ABCD"}, # [cite: 15]
    {"id": "08_m4", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 4, "question": "4.中国特色社会主义政治制度的巨大优势体现在（  ）。", "options": {"A":"能够有效保证人民享有更加广泛的权利和自由", "B":"能够有效调节国家政治关系，形成安定团结的政治局面", "C":"能够集中力量办大事，有效促进社会生产力解放和发展", "D":"能够有效维护国家独立自主,有力维护国家主权、安全、发展利益"}, "answer": "ABCD"}, # [cite: 15]
    {"id": "08_m5", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 5, "question": "5.中华人民共和国的一切权力属于人民，人民行使国家权力的机关是（）。", "options": {"A":"全国人民代表大会", "B":"地方各级人民代表大会", "C":"国务院", "D":"人民代表"}, "answer": "AB"}, # [cite: 15]
    {"id": "08_m6", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 6, "question": "6.人民代表大会制度（  ）。", "options": {"A":"坚持中国共产党领导，有效保证国家沿着社会主义道路前进", "B":"最大限度保障人民当家作主", "C":"有效保证国家治理跳出治乱兴衰的历史周期率", "D":"正确处理事关国家前途命运的一系列重大政治关系，维护国家统一和民族团结", "E":"有效保证国家政治生活既充满活力又安定有序。"}, "answer": "ABCDE"}, # [cite: 15]
    {"id": "08_m7", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 7, "question": "7.全过程人民民主是最真实的民主,具体体现在（ ）。", "options": {"A":"把党的主张、国家意志、人民意愿紧密融合在一起，彰显了人民民主的真实性", "B":"真实反映人民的期盼、希望和诉求", "C":"人民的意愿和呼声，经过民主决策程序成为党和国家的方针政策", "D":"真真切切落实到国家政治生活和社会生活各方面"}, "answer": "ABCD"}, # [cite: 15]
    {"id": "08_m8", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 8, "question": "8.全过程人民民主是最广泛的民主, 具体体现在（ ）。", "options": {"A":"人民既充分享有民主选举权利，又充分享有民主协商、民主决策、民主管理、民主监督权利", "B":"既参与国家事务管理，又参与经济和文化事业以及社会事务管理", "C":"既参与国家发展顶层设计的意见建议征询，又参与地方公共事务治理", "D":"不同地域、不同领域、不同层级、不同群体均实现全面覆盖"}, "answer": "ABCD"}, # [cite: 15]
    {"id": "08_m9", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 9, "question": "9.全过程人民民主是最管用的民主, 具体体现在（ ）。", "options": {"A":"保证在党的领导下有效治理国家，切实防止出现一盘散沙的现象", "B":"保证人民依法行使权利，切实防止出现选举时漫天许诺、选举后无人过问的现象", "C":"加强社会各种力量的合作协调，切实防止出现党争纷沓、相互倾轧的现象", "D":"巩固平等团结互助和谐的社会主义民族关系，切实防止出现民族隔阂、民族冲突的现象", "E":"发展基层民主，切实防止出现人民形式上有权、实际上无权的现象"}, "answer": "ABCDE"}, # [cite: 15]
    {"id": "08_m10", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 10, "question": "10.我国的协商民主体系包括（  ）。", "options": {"A":"政党协商，人大协商", "B":"政府协商", "C":"人民团体协商", "D":"政协协商、", "E":"基层协商以及社会组织协商"}, "answer": "ABCDE"}, # [cite: 15, 16]
    {"id": "08_m11", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 11, "question": "11.我国基层民主有多种多样的形式，如(   )。", "options": {"A":"以村民委员会为组织形态的农村村民自治", "B":"以社区居民委员会为组织形态的城市居民自治", "C":"以职工代表大会为组织依托的企事业单位职工自治", "D":"以上都对"}, "answer": "ABCD"}, # [cite: 16]
    {"id": "08_m12", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 12, "question": "12.统一战线工作的本质要求是（    ）。", "options": {"A":"大团结大联合", "B":"解决的就是人心和力量问题", "C":"推进国家统一", "D":"实现中华民族伟大复兴"}, "answer": "AB"}, # [cite: 16]
    {"id": "08_m13", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 13, "question": "13.铸牢中华民族共同体意识，就要（    ）。", "options": {"A":"要引导各族人民牢固树立休戚与共、荣辱与共、命运与共的共同体理念", "B":"要正确把握共同性和差异性的关系、中华民族共同体意识和各民族意识的关系、中华文化和各民族文化的关系", "C":"建设各民族共有精神家园，促进各民族共同繁荣共同发展", "D":"引导各族群众牢固树立正确的祖国观、民族观、文化观、历史观"}, "answer": "ABCD"}, # [cite: 16]
    {"id": "08_m14", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 14, "question": "14.统一战线工作范围包括（    ）。", "options": {"A":"民主党派成员，无党派人士，党外知识分子", "B":"少数民族人士，宗教界人士", "C":"非公有制经济人士，新的社会阶层人士", "D":"出国和归国留学人员", "E":"香港同胞，澳门同胞，台湾同胞，华侨归侨及侨眷"}, "answer": "ABCDE"}, # [cite: 16] # Original answer was ABCDE without separating options.
    {"id": "08_m15", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 15, "question": "15.全过程人民民主是（   ）的民主，是最广泛、最真实、最管用的社会主义民主。", "options": {"A":"全方面", "B":"全链条", "C":"全方位", "D":"全覆盖"}, "answer": "BCD"}, # [cite: 16]
    {"id": "08_m16", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 16, "question": "16.全过程人民民主实现了（    ）。", "options": {"A":"过程民主和成果民主相统一", "B":"程序民主和实质民主相统一", "C":"直接民主和间接民主相统一", "D":"人民民主和国家意志相统一"}, "answer": "ABCD"}, # [cite: 16]
    {"id": "08_m17", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 17, "question": "17. 在人民民主的共同旗帜下，中国共产党与各民主党派（   ）。", "options": {"A":"长期共存", "B":"互相监督", "C":"肝胆相照", "D":"荣辱与共"}, "answer": "ABCD"}, # [cite: 16]
    {"id": "08_m18", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 18, "question": "18.巩固和发展爱国统一战线，应该着手做好以下工作（ ）。", "options": {"A":"坚持长期共存、互相监督、肝胆相照、荣辱与共的中国共产党领导的政治协商制度", "B":"深化民族团结进步教育", "C":"全面贯彻党的宗教工作基本方针", "D":"牢牢把握大团结大联合的主题，做好统战工作"}, "answer": "ABCD"}, # [cite: 16, 17]
    {"id": "08_m19", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 19, "question": "19.走中国特色社会主义政治发展道路，必须坚持（ ）有机统一。", "options": {"A":"推进国家治理体系和治理能力现代化", "B":"巩固和发展最广泛的爱国统一战线", "C":"党的领导", "D":"人民当家作主 ，依法治国"}, "answer": "CD"}, # [cite: 17] # This combines C and D.
    {"id": "08_m20", "type": "multiple", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 20, "question": "20.全过程人民民主是社会主义民主政治的本质属性，是(   )的民主。", "options": {"A":"最广泛", "B":"最真实", "C":"最管用", "D":"最典型"}, "answer": "ABC"}, # [cite: 17]
    # Judgment (判断题) from 08.doc
    {"id": "08_j1", "type": "judgment_as_single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 1, "question": "坚持走中国特色社会主义政治发展道路，全面发展全过程人民民主，社会主义民主政治制度化、规范化、程序化全面推进。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 17]
    {"id": "08_j2", "type": "judgment_as_single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 2, "question": "人民民主是社会主义的生命，没有民主就没有社会主义。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 17]
    {"id": "08_j3", "type": "judgment_as_single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 3, "question": "中国共产党领导的多党合作和政治协商制度、民族区域自治制度以及基层群众自治制度构成我国的根本政治制度。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 17]
    {"id": "08_j4", "type": "judgment_as_single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 4, "question": "我国的各项国家制度都是围绕人民当家作主构建的，国家治理体系都是围绕实现人民当家作主运转的。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 17]
    {"id": "08_j5", "type": "judgment_as_single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 5, "question": "民主就是指民主选举，不搞“一人一票”竞选就是“不民主”。", "options": {"A": "正确", "B": "错误"}, "answer": "B"}, # [cite: 17]
    {"id": "08_j6", "type": "judgment_as_single", "source_doc": "08.doc", "doc_order": 8, "q_num_in_doc": 6, "question": "6.做统战工作要把握好固守圆心和扩大共识、潜绩和显绩、原则性和灵活性、团结和斗争的关系。", "options": {"A": "正确", "B": "错误"}, "answer": "A"}, # [cite: 17]

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
    {"id": "13_m7", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 7, "question": "7.对发展和安全的理解，正确的观点是（ ）。", "options": {"A":"发展解决的是动力问题，是推动国家和民族康续绵延的根本支撑", "B":"安全解决的是保障问题，是确保国家和民族行稳致远的坚强柱石", "C":"发展具有基础性、根本性，是解决安全问题的总钥匙", "D":"没有国家安全,发展取得的成果也可能毁于一旦", "E":"发展和安全是一体之两翼、驱动之双轮，必须同步推进"}, "answer": "ABCDE"}, # [cite: 13]
    {"id": "13_m8", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 8, "question": "8.对新安全格局和新发展格局关系的正确理解是（   ）。", "options": {"A":"新安全格局是新发展格局的重要前提和保障。", "B":"只有以新安全格局保障新发展格局，才能夯实我国经济发展的根基、增强发展的安全性稳定性", "C":"只有以新安全格局保障新发展格局，才能在各种可以预见和难以预见的风险挑战中增强我国的生存力、竞争力、发展力、持续力", "D":"以新安全格局保障新发展格局，必须统筹维护国家安全各类要素、各方资源、各种手段，主动塑造有利的外部安全环境"}, "answer": "ABCD"}, # [cite: 13]
    {"id": "13_m9", "type": "multiple", "source_doc": "13.doc", "doc_order": 13, "q_num_in_doc": 9, "question": "9.政治安全涉及国家（   ）的稳固，是一个国家最根本的需求。", "options": {"A":"主权", "B":"政权", "C":"制度", "D":"意识形态"}, "answer": "ABCD"}, # [cite: 13]
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
    {"id": "15_m13", "type": "multiple", "source_doc": "15.doc", "doc_order": 15, "q_num_in_doc": 13, "question": "13.牢牢把握两岸关系主导权和主动权，要做到（ ）。", "options": {"A":"坚持“和平统一、一国两制”方针，探索“两制”台湾方案", "B":"坚定支持岛内爱国统一力量，坚定反“独”促统", "C":"促进两岸经济文化交流合作，深化两岸各领域融合发展", "D":"坚持以最大诚意、尽最大努力争取和平统一的前景，但决不承诺放弃使用武力"}, "answer": "ABCD"}, # [cite: 25]
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
    {"id": "16_m8", "type": "multiple", "source_doc": "16.doc", "doc_order": 16, "q_num_in_doc": 8, "question": "8.中国特色大国外交的独特风范表现在（ ）。", "options": {"A":"坚持马克思主义立场观点方法,从中华优秀传统文化中汲取智慧", "B":"坚持爱国主义同国际主义相结合", "C":"倡导不同社会制度和发展道路相互包容", "D":"坚持诚信为本，始终恪守政治承诺", "E":"倡导不同国家、不同民族、不同文明互学互鉴"}, "answer": "ABCDE"}, # [cite: 30]
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
    {"id": "17_m16", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 16, "question": "16.对中国共产党是世界上最大的马克思主义执政党，解决大党独有难题，要（ ）。", "options": {"A":"加强党的政治建设", "B":"深化理论武装", "C":"推动高质量发展", "D":"维护党的团结和集中统一"}, "answer": "ABCD"}, # [cite: 37]
    {"id": "17_m17", "type": "multiple", "source_doc": "17.doc", "doc_order": 17, "q_num_in_doc": 17, "question": "17. 之所以要把党的政治建设摆在首位，是因为（   ）。", "options": {"A":"党的政治建设是根本性建设，决定党的建设的方向和效果", "B":"只有党的政治建设抓好了，党的建设才能夯基固本", "C":"坚持和加强党的全面领导，确保党始终成为坚强领导核心", "D":"增强“四个意识”、坚定“四个自信”、做到“两个维护”"}, "answer": "ABCD"}, # [cite: 37]
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
        raw_wrong_answers = db_manager.get_wrong_answers(user_id)
        processed_wrong_answers = []
        for ans_row in raw_wrong_answers:
            # Convert sqlite3.Row to a mutable dict to modify it
            processed_ans = dict(ans_row) 
            if 'last_wrong_at' in processed_ans and isinstance(processed_ans['last_wrong_at'], str):
                original_date_str = processed_ans['last_wrong_at']
                try:
                    # Try parsing with fractional seconds first, then without
                    try:
                        processed_ans['last_wrong_at'] = datetime.strptime(original_date_str, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        processed_ans['last_wrong_at'] = datetime.strptime(original_date_str, '%Y-%m-%d %H:%M:%S')
                except ValueError as e_parse:
                    logger.warning(f"Could not parse date string '{original_date_str}' for question_id {processed_ans.get('question_id')}: {e_parse}. Setting to None.")
                    processed_ans['last_wrong_at'] = None # Ensure it's None if parsing fails
            processed_wrong_answers.append(processed_ans)
        
        stats = db_manager.get_wrong_answer_stats(user_id)
        
        # Make sure to pass the processed list to the template
        return render_template('wrong_answers.html', 
                             username=session.get('username'),
                             wrong_answers=processed_wrong_answers, 
                             stats=stats)
    except Exception as e:
        logger.error(f"获取错题本失败: {e}")
        import traceback
        logger.error(traceback.format_exc()) # Log full traceback for better debugging
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
        
        question_options_data = data['question_options']
        if isinstance(question_options_data, str):
            try:
                question_options_parsed = json.loads(question_options_data)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse question_options JSON: {question_options_data}")
                return jsonify({'message': '选项数据格式错误'}), 400
        else:
            question_options_parsed = question_options_data

        db_manager.add_wrong_answer(
            user_id=user_id,
            question_id=data['question_id'],
            question_text=data['question_text'],
            question_type=data['question_type'],
            correct_answer=data['correct_answer'],
            user_answer=data['user_answer'],
            question_options=question_options_parsed, # Pass the parsed dictionary
            source_doc=data.get('source_doc', '') # Use .get for optional fields
        )
        
        return jsonify({'message': '错题记录成功'}), 200
        
    except KeyError as e:
        logger.error(f"记录错题失败: 缺少字段 {e}")
        return jsonify({'message': f'记录错题失败，缺少字段: {e}'}), 400
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

from otree.api import *

"""
两套实验逻辑系统说明：
====================
1. 实验顺序固定：第一轮使用逻辑1，第二轮使用逻辑2
2. 在任何页面中，可以通过 player.current_logic 获取当前轮次应该使用的逻辑编号（1或2）
3. 在HTML模板中，可以通过 {% if current_logic == 1 %} 来显示不同的内容
4. 当前代码中的内容为第一套逻辑（逻辑1），第二套逻辑（逻辑2）待实现

使用方法：
- 在页面类中添加 vars_for_template 方法，返回 {'current_logic': player.current_logic}
- 在HTML模板中使用 {% if current_logic == 1 %} 和 {% else %} 来显示不同内容
- 在Python代码中，使用 player.current_logic 来判断应该执行哪套逻辑
"""


class C(BaseConstants):
    NAME_IN_URL = 'public_goods_corrupt'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 2
    ENDOWMENT = cu(20)
    MULTIPLIER = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()
    # 存储该组在第一轮使用的实验逻辑编号（1或2）
    starting_logic = models.IntegerField(initial=1)


class Player(BasePlayer):
    # 知情同意字段
    consent = models.BooleanField(
        label="我已阅读并同意参加本研究"
    )
    # 被试编号字段（限定为数字）
    subject_id = models.IntegerField(
        label="请输入你的被试编号："
    )
    # 玩家角色字段（A、B、C 或 D）
    player_role = models.StringField()
    # 理解检查问题1：公共池倍率（选择题，正确答案为2）
    comprehension_q1 = models.IntegerField(
        label="（1）公共池的倍率为多少？",
        choices=[
            [1, 'A. 1'],
            [2, 'B. 2'],
            [3, 'C. 3'],
            [4, 'D. 4'],
        ],
        widget=widgets.RadioSelect
    )
    # 理解检查问题2：角色数量（选择题，正确答案为5）
    comprehension_q2 = models.IntegerField(
        label="（2）每组中共有几个角色？",
        choices=[
            [1, 'A. 2'],
            [2, 'B. 3'],
            [3, 'C. 4'],
            [4, 'D. 5'],
        ],
        widget=widgets.RadioSelect
    )
    # 理解检查问题3：最终获得代币数（填空题，正确答案为3）
    comprehension_q3 = models.IntegerField(
        label='''（3）E的1代币可以增加/减少A、B、C或D的多少代币？''',
        choices=[
            [1, 'A. 1'],
            [2, 'B. 2'],
            [3, 'C. 3'],
            [4, 'D. 4'],
        ],
        widget=widgets.RadioSelect
    )
    # 原有的贡献字段
    contribution = models.IntegerField(
    min=0, max=C.ENDOWMENT, label="你选择投入公共池的代币数为：")

    # 转给玩家E的代币数（第二套逻辑使用）
    transfer_to_e = models.IntegerField(
        min=0, max=C.ENDOWMENT, label="你选择转给玩家E的代币数为: ")

    # 反应时字段（毫秒）：从看到投资决策页面到提交决策的时间
    reaction_time = models.FloatField(initial=0)
    # 页面加载时间戳
    page_load_time = models.FloatField(initial=0)
    
    # 情绪评估字段（1-7量表，1=非常消极，7=非常积极）
    emotion_state = models.IntegerField(
        label="此时你的情绪状态为？",
        choices=[
            [1, '1 - 非常消极'],
            [2, '2 - 比较消极'],
            [3, '3 - 有点消极'],
            [4, '4 - 不消极也不积极'],
            [5, '5 - 有点积极'],
            [6, '6 - 比较积极'],
            [7, '7 - 非常积极'],
        ],
        widget=widgets.RadioSelect
    )
    
    @property
    def role(self):
        """返回玩家角色，用于模板显示"""
        return self.player_role
    
    @property
    def current_logic(self):
        """返回当前轮次应该使用的实验逻辑编号（1或2）
        第一轮固定使用逻辑1，第二轮固定使用逻辑2"""
        if self.round_number == 1:
            return 1
        else:
            return 2


# FUNCTIONS
def creating_session(subsession: Subsession):
    """为每个玩家分配角色 A、B、C 或 D（共5种角色ABCDE可以抽取，但实际只分配ABCD）；第2轮沿用第1轮角色与分组
    实验顺序固定：第一轮使用逻辑1，第二轮使用逻辑2"""
    import random
    roles = ['A', 'B', 'C', 'D']
    
    # 第2轮起保持与第1轮相同的分组（确保角色位置一致）
    if subsession.round_number > 1:
        subsession.group_like_round(1)
    
    for group in subsession.get_groups():
        players = group.get_players()
        
        if subsession.round_number == 1:
            # 第1轮：固定使用逻辑1，设置group.starting_logic为1（保持兼容性）
            group.starting_logic = 1
            
            # 第1轮：随机打乱并分配角色
            assigned_roles = roles.copy()
            random.shuffle(assigned_roles)
            for i, player in enumerate(players):
                player.player_role = assigned_roles[i]
                # 缓存玩家角色，供后续轮次继承
                player.participant.vars['player_role'] = player.player_role
        else:
            # 第2轮及以后：固定使用逻辑2，设置group.starting_logic为2（保持兼容性）
            group.starting_logic = 2
            
            # 第2轮及以后：沿用玩家在第1轮的角色
            for player in players:
                stored_role = player.participant.vars.get('player_role')
                if stored_role:
                    player.player_role = stored_role
        
        # 跨轮次继承被试编号
        if subsession.round_number > 1:
            for player in players:
                stored_subject_id = player.participant.vars.get('subject_id')
                if stored_subject_id is not None:
                    player.subject_id = stored_subject_id


def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
    )
    for p in players:
        p.payoff = C.ENDOWMENT - p.contribution + group.individual_share


# PAGES
class ConsentPage(Page):
    """知情同意页面：只在第一轮显示"""
    form_model = 'player'
    form_fields = ['consent']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        if not values.get('consent'):
            return '只有同意参加实验才能进入实验'


class ParticipantID(Page):
    """第一页：输入被试编号"""
    form_model = 'player'
    form_fields = ['subject_id']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['subject_id'] = player.subject_id


class Instructions(Page):
    """第二页：实验背景介绍"""
    
    @staticmethod
    def vars_for_template(player: Player):
        """传递当前逻辑编号到模板，方便根据逻辑显示不同内容"""
        return {
            'current_logic': player.current_logic
        }


class ComprehensionCheck(Page):
    """第三页：理解检查"""
    form_model = 'player'
    form_fields = ['comprehension_q1', 'comprehension_q2', 'comprehension_q3']
    
    def error_message(self, values):
        """验证答案是否正确"""
        errors = []
        
        # 检查问题1：公共池倍率，正确答案为2
        if values.get('comprehension_q1') != 2:
            errors.append('问题1答案不正确，请重新回答。')
        
        # 检查问题2：角色数量，正确答案为5
        if values.get('comprehension_q2') != 4:
            errors.append('问题2答案不正确，请重新回答。')
        
        # 检查问题3：最终获得代币数，正确答案为3
        if values.get('comprehension_q3') != 3:
            errors.append('问题3答案不正确，请重新回答。')
        
        if errors:
            return ' '.join(errors)


class ComprehensionWaitPage(WaitPage):
    """理解检验后等待页面"""
    title_text = "等待其他玩家"
    body_text = "请稍候，等待其他玩家完成理解检验并加入游戏..."


class MatchingWaitPage(Page):
    """匹配等待页面"""
    timeout_seconds = 4
    title_text = "正在匹配其他玩家"
    body_text = "请稍候，正在为你匹配其他玩家..."


class MatchingSuccess(Page):
    """匹配成功页面"""
    timeout_seconds = 4


class Contribute(Page):
    """第四页：公共品博弈环节"""
    form_model = 'player'
    # 动态按逻辑返回表单字段，避免隐藏字段导致的校验阻塞
    def get_form_fields(player: Player):
        if player.current_logic == 1:
            return ['contribution', 'reaction_time', 'page_load_time']
        return ['contribution', 'transfer_to_e', 'reaction_time', 'page_load_time']
    
    @staticmethod
    def vars_for_template(player: Player):
        return {
            'player_role': player.role,
            'current_logic': player.current_logic
        }
    
    @staticmethod
    def error_message(player: Player, values):
        """验证表单数据"""
        if player.current_logic == 2:
            # 第二套逻辑：验证投给公共池和转给E的币数总和不超过20
            contribution = values.get('contribution', 0) or 0
            transfer_to_e = values.get('transfer_to_e', 0) or 0
            total = contribution + transfer_to_e
            
            if total > C.ENDOWMENT:
                return f'你投入公共池的代币数（{contribution}）和转给玩家E的代币数（{transfer_to_e}）的总和（{total}）不能超过{C.ENDOWMENT}个代币。请重新分配。'
        else:
            # 第一套逻辑：确保transfer_to_e为0（如果被意外设置）
            if values.get('transfer_to_e', 0):
                values['transfer_to_e'] = 0
        
        return None


class ResultsWaitPage(WaitPage):
    title_text = "等待其他玩家"
    body_text = "请稍候，等待其他玩家完成决策..."
    after_all_players_arrive = set_payoffs


class PlayerEWaitPage(Page):
    timeout_seconds = 6

    @staticmethod
    def is_displayed(player: Player):
        return True
        # 如果只在某套逻辑下显示：
        # return player.current_logic == 1


class EmotionAssessment(Page):
    """情绪评估页面：在每轮投资决策后询问情绪状态"""
    form_model = 'player'
    form_fields = ['emotion_state']


class Results(Page):
    """结果页面：显示感谢和截图提醒"""

    @staticmethod
    def vars_for_template(player: Player):
        stored_subject_id = player.field_maybe_none('subject_id')
        if stored_subject_id is None:
            stored_subject_id = player.participant.vars.get('subject_id')
            if stored_subject_id is not None:
                player.subject_id = stored_subject_id
        return dict(subject_id=stored_subject_id)


class ThankYou(Page):
    """最后一页：感谢页"""
    pass


page_sequence = [
    ConsentPage,
    ParticipantID, 
    Instructions, 
    ComprehensionCheck, 
    ComprehensionWaitPage,
    MatchingWaitPage,
    MatchingSuccess,
    Contribute, 
    EmotionAssessment,
    ResultsWaitPage,
    PlayerEWaitPage,
    Results,
]

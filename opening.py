from dialogue_flow import DialogueFlow, HIGHSCORE, LOWSCORE
from datetime import datetime
from data import names, positive_indicators, negative_indicators, feelings_positive, \
                    feelings_negative, feelings_neutral, downers, uppers, negative, negation

component = DialogueFlow('prestart')

standard_opening = "Hi this is an Alexa Prize Socialbot."
inquire_feeling = "How are you today?"

arcs = []

arcs.extend([(f, 'feelings_positive', 'type') for f in feelings_positive])
arcs.extend([(f, 'feelings_negative', 'type') for f in feelings_negative])
arcs.extend([(f, 'feelings_neutral', 'type') for f in feelings_neutral])
arcs.extend([(f, 'downers', 'type') for f in downers])
arcs.extend([(f, 'uppers', 'type') for f in uppers])
arcs.extend([(f, 'negative', 'type') for f in negative])
arcs.extend([(f, 'positive_indicators', 'type') for f in positive_indicators])
arcs.extend([(f, 'negative_indicators', 'type') for f in negative_indicators])
arcs.extend([(f, 'negation', 'type') for f in negation])
arcs.extend([(x, 'names', 'type') for x in names])
arcs.extend([])
for arc in arcs:
    component.knowledge_base().add(*arc)

def check_launch_request(arg_dict):
    if arg_dict:
        if arg_dict["request_type"] == "LaunchRequest":
            return HIGHSCORE, {}
    return 0, {}

def check_new(arg_dict):
    if arg_dict:
        if "prev_conv_date" not in arg_dict or arg_dict["prev_conv_date"] is None:
            return HIGHSCORE, {}
    return 0, {}

def check_infreq(arg_dict):
    if arg_dict:
        if "prev_conv_date" in arg_dict and arg_dict["prev_conv_date"] is not None:
            old_datetime = datetime.strptime(arg_dict["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f')
            delta = datetime.today() - old_datetime
            if delta.days >= 7:
                return HIGHSCORE, {}
    return 0, {}

def check_freq(arg_dict):
    if arg_dict:
        if "prev_conv_date" in arg_dict and arg_dict["prev_conv_date"] is not None:
            old_datetime = datetime.strptime(arg_dict["prev_conv_date"], '%Y-%m-%d %H:%M:%S.%f')
            delta = datetime.today() - old_datetime
            if delta.days < 7:
                return HIGHSCORE, {}
    return 0, {}

def is_new_user(arg_dict, score, vars):
    score, vars = check_launch_request(arg_dict)
    if score == HIGHSCORE:
        score, vars = check_new(arg_dict)
        if score == HIGHSCORE:
            return HIGHSCORE, {}
    return 0, {}

def is_infreq_user(arg_dict, score, vars):
    score, vars = check_launch_request(arg_dict)
    if score == HIGHSCORE:
        score, vars = check_infreq(arg_dict)
        if score == HIGHSCORE:
            return HIGHSCORE, {}
    return 0, {}

def is_freq_user(arg_dict, score, vars):
    score, vars = check_launch_request(arg_dict)
    if score == HIGHSCORE:
        score, vars = check_freq(arg_dict)
        if score == HIGHSCORE:
            return HIGHSCORE, {}
    return 0, {}


# pre start
component.add_transition(
    'prestart', 'prestart', None, {'x'}, settings='e'
)

# start: new user

component.add_transition(
    'prestart', 'start_new',
    None, {}, evaluation_transition=is_new_user
)

# start: infrequent user

component.add_transition(
    'prestart', 'start_infreq',
    None, {}, evaluation_transition=is_infreq_user
)

# start: frequent user

component.add_transition(
    'prestart', 'start_freq',
    None, {}, evaluation_transition=is_freq_user
)

component.add_transition(
    'start_new', 'receive_name',
    None, {standard_opening + " What can I call you?"}
)

component.add_transition(
    'receive_name', 'missed_name',
    None, {"i dont want to tell you"}
)

component.add_transition(
    'missed_name', 'acknowledge_name',
    None, {"Its very nice to meet you."}
)

component.add_transition(
    'receive_name', 'got_name',
    '%username=&names', {"i am an alexa prize socialbot"}
)

component.add_transition(
    'got_name', 'how_are_you',
    None, {"Nice to meet you, $username. " + inquire_feeling:0.999, "Nice to meet you. " + inquire_feeling:0.001}
)

component.add_transition(
    'start_freq', 'how_are_you',
    None,
    {standard_opening + " Welcome back, $username. " + inquire_feeling: 0.999,
     standard_opening + " Welcome back, im excited to talk to you again. " + inquire_feeling: 0.001},
    evaluation_transition=is_freq_user

)

component.add_transition(
    'start_infreq', 'how_are_you',
    None,
    {standard_opening + " Its good to see you again, $username, its been a while since we last chatted. " + inquire_feeling: 0.999,
     standard_opening + " Its good to see you again, its been a while since we last chatted. " + inquire_feeling: 0.001},
    evaluation_transition=is_infreq_user
)

component.add_transition(
    'how_are_you', 'feeling_pos',
    '{'
    '<-&negation, (&feelings_positive)>,'
    '(&negation, &feelings_negative)'
    '}',
    {"im good"}
)

component.add_transition(
    'how_are_you', 'feeling_neg',
    '{'
    '<-&negation, (&feelings_negative)>,'
    '(&negation, {&feelings_positive,&feelings_neutral})'
    '}',
    {"im bad"}
)

component.add_transition(
    'how_are_you', 'feeling_neutral',
    '{'
    '<-&negation, (&feelings_neutral)>'
    '}',
    {"im ok"}
)

component.add_transition(
    'how_are_you', 'unrecognized_emotion',
    None,
    {"im trying"},
    settings = 'e'
)

component.add_transition(
    'how_are_you', 'decline_share',
    '{'
    '<-&negation, ({talk, discuss, share})>,'
    '(&negative)'
    '}',
    {"i dont want to talk about it"}
)

component.add_transition(
    'unrecognized_emotion', 'end',
    None,
    {"Hmm, I'm not sure what you mean."},
    settings = 'e'
)

component.add_transition(
    'feeling_pos', 'acknowledge_pos',
    None,
    {"Im glad to hear that. What has caused your good mood?"}
)

component.add_transition(
    'feeling_neg', 'acknowledge_neg',
    None,
    {"Im sorry thats how you feel today. If you don't mind talking about it, what happened?"}
)

component.add_transition(
    'feeling_neutral', 'acknowledge_neutral',
    None,
    {"That's understandable. Is there anything in particular that made you feel this way?"}
)

# expand REGEX
component.add_transition(
    'acknowledge_pos', 'share_pos',
    '{'
    '<-&negation, (&positive_indicators)>'
    '}',
    {"i just had a good day with my family yesterday"}
)

component.add_transition(
    'acknowledge_neutral', 'share_pos',
    '{'
    '<-&negation, (&positive_indicators)>'
    '}',
    {"i just had a good day with my family yesterday"}
)

component.add_transition(
    'acknowledge_neg', 'share_neg',
    '{'
    '(&negation, &positive_indicators),'
    '(&negative_indicators)'
    '}',
    {"i didnt sleep well last night"}
)

component.add_transition(
    'acknowledge_neutral', 'share_neg',
    '{'
    '(&negation, &positive_indicators),'
    '(&negative_indicators)'
    '}',
    {"i didnt sleep well last night"}
)

component.add_transition(
    'acknowledge_pos', 'decline_share',
    '{'
    '<-&negation, ({talk, discuss, share})>,'
    '(&negative)'
    '}'
    ,
    {"i dont want to talk about it"}
)

component.add_transition(
    'acknowledge_neg', 'decline_share',
    '{'
    '<-&negation, ({talk, discuss, share})>,'
    '(&negative)'
    '}',
    {"i dont want to talk about it"}
)

component.add_transition(
    'acknowledge_neutral', 'decline_share',
    '{'
    '<-&negation, ({talk, discuss, share})>,'
    '(&negative)'
    '}',
    {"i dont want to talk about it"}
)

component.add_transition(
    'acknowledge_pos', 'misunderstood',
    None,
    {"just stuff"},
    settings = 'e'
)

component.add_transition(
    'acknowledge_neg', 'misunderstood',
    None,
    {"just stuff"},
    settings = 'e'
)

component.add_transition(
    'acknowledge_neutral', 'misunderstood',
    None,
    {"just stuff"},
    settings = 'e'
)

component.add_transition(
    'misunderstood', 'end',
    None,
    {"Thanks for sharing that with me."}
)

component.add_transition(
    'share_pos', 'acknowledge_share_pos',
    None,
    {"Sounds really nice, thanks for sharing that with me. I love hearing about your life."}
)

component.add_transition(
    'share_neg', 'acknowledge_share_neg',
    None,
    {"I think that sounds really unfortunate, I hope it gets better for you soon."}
)

component.add_transition(
    'decline_share', 'acknowledge_decline_share',
    None,
    {"That's ok, I'm happy to talk about other things too."}
)

component.add_transition(
    'acknowledge_share_pos', 'end',
    None,
    {"thats cool"}
)

component.add_transition(
    'acknowledge_share_neg', 'end',
    None,
    {"thats cool"}
)

component.add_transition(
    'acknowledge_decline_share', 'end',
    None,
    {"thats cool"}
)

component.add_transition(
    'garbage', 'end',
    None, {'thats cool'}
)

component.add_transition(
    'end', 'end', None, {'x'}, settings='e'
)

if __name__ == '__main__':
    i = input('U: ')
    while True:
        arg_dict = {"prev_conv_date": "2020-1-8 16:55:33.562881", "username": "sarah"}
        arg_dict2 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": "sarah"}
        arg_dict3 = {"prev_conv_date": "2019-12-12 16:55:33.562881", "username": None}
        arg_dict4 = {"prev_conv_date": None, "stat": "Ive met quite a few people with your name recently."}
        if i == "hello":
            arg_dict["request_type"] = "LaunchRequest"
            arg_dict2["request_type"] = "LaunchRequest"
            arg_dict3["request_type"] = "LaunchRequest"
            arg_dict4["request_type"] = "LaunchRequest"

        using = arg_dict2
        component.vars().update({key: val for key, val in using.items() if val is not None})

        confidence = component.user_transition(i) / 10 - 0.3
        print(component.state(), component.vars())
        if component.state() == "end":
            break

        print('({}) '.format(confidence), component.system_transition())
        if component.state() == "end":
            print(component.state(), component.vars())
            break
        i = input('U: ')
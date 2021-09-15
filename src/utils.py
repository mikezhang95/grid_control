
import copy
import numpy as np

NUM_GEN = 54

# M: Notice the normalize function in Baselines. We should carefully set low and high value
# https://github.com/hill-a/stable-baselines/blob/master/stable_baselines/common/input.py


################################# 9.5 ##############################
"""
### 向量化obs: 
    - gen_p: 54, [-1,1] // normalized by curtime's max abs value
    - gen_q: 54, [-1,1] // normalized by curtime's max abs value
    - gen_v: 54, [0,1] // normalized by curtime's max abs value
    - gen_status: 54, {0,1}
    - steps_to_recover_gen: 54, [0,0.4] // normalized by 100
    - steps_to_close_gen: 54, [0,0.4] // normalized by 100
    - renewable_gen_p_max_diff: 54, [-1,1] // normalized by curtime's max abs value
    - load_p_diff: 91, [-1,1] // normalized by curtime's max abs value
    - load_q: 91, [-1,1] // normalized by curtime's max abs value
    - load_v: 91, [0,1] // normalized by curtime's max abs value  
M: (1) 归一化变量用的是当前时刻的最大值，time dependent (2) 有一些变量用的diff，有一些用的绝对值 (3) 缺少每个bus节点的信息
"""
def vec_obs(obs):
    """
        Convert obs to array-like observation, range [-1,1]
    """
    new_obs = []
    # gen_p, gen_q, gen_v: 机组发电
    new_obs.extend(obs.gen_p / max(np.max(np.abs(obs.gen_p)), 1e-7) )
    new_obs.extend(obs.gen_q / max(np.max(np.abs(obs.gen_q)), 1e-7) )
    new_obs.extend(obs.gen_v / max(np.max(np.abs(obs.gen_v)), 1e-7) )

    # gen status, steps_to_recover_gen, steps_to_close_gen: 机组状态, int类型
    new_obs.extend(list(obs.gen_status))
    new_obs.extend( list(obs.steps_to_recover_gen / 100.) )
    new_obs.extend( list(obs.steps_to_close_gen / 100.) )
    # print (f"This is the gen_status: {obs.gen_status}")
    # print (f"This is the steps to recover gen: {obs.steps_to_recover_gen}")
    # print (f"This is the steps to close gen: {obs.steps_to_close_gen}")

    # curstep_renewable_gen_p_max, nextstep_newable_gen_p_max: 新能源发电
    # new_obs.extend(obs.curstep_renewable_gen_p_max)
    # new_obs.extend(obs.nextstep_renewable_gen_p_max)
    renewable_gen_p_max_diff = np.array(obs.nextstep_renewable_gen_p_max) - np.array(obs.curstep_renewable_gen_p_max)
    new_obs.extend( ( renewable_gen_p_max_diff / max(np.max(np.abs(renewable_gen_p_max_diff)), 1e-7) ).tolist() )

    # load_p, load_q, load_v, nextstep_load_p: 负荷耗电
    # new_obs.extend(obs.load_p)
    # new_obs.extend(obs.nextstep_load_p)
    new_obs.extend( obs.load_q / max(np.max(np.abs(obs.load_q)), 1e-7) )
    new_obs.extend( obs.load_v / max(np.max(np.abs(obs.load_v)), 1e-7) )
    load_p_diff = np.array(obs.nextstep_load_p) - np.array(obs.load_p)
    new_obs.extend( ( load_p_diff / max(np.max(np.abs(load_p_diff)), 1e-7) ).tolist() )

    observation = np.array(new_obs).astype(np.float32)
    return observation

################################# 9.5 ##############################
"""
### 反向量化action: 
    - adjust_gen_p: [-0.05, 0.05] // use tanh to squash, then clip by legal_act_space
    - adjust_gen_v: [-0.0, 1.0] // use tanh to squash, then clip by legal_act_space
"""
def unvec_action(action, legal_act_space):
    """
        Convert array-like action (range [-1,1]) to act
    """
    action = np.array(action).flatten().astype(np.float32)
    act_dim = action.shape[0] // 2
    act = {"adjust_gen_p": action[:act_dim] * 0.05,
           "adjust_gen_v": action[act_dim:] * 0.5 + 0.5}
    act = clip_act(act, legal_act_space)
    return act

def clip_act(act, legal_act_space):
    new_act = {}
    for k, v in act.items():
        low_bound = legal_act_space[k].low
        high_bound = legal_act_space[k].high
        # unscaled_act = (v + 1) / 2.0 * (high_bound - low_bound) + low_bound
        unscaled_act = np.clip(v, low_bound, high_bound)
        new_act[k] = unscaled_act
    return new_act

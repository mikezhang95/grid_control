

# Environment Description

每个节点上面可以连接若干发电(机组)和用电(负荷)设备，节点之间由线路连接。需要通过控制发电设备的功率和电压让电网达到平衡。          
> 机组(发电) 54 / 新能源机组 18 / 负荷(用电) 91 / 线路(支路) 185 / 节点 126


### Environment     

* settings
* forecast_reader: ForecastReader从表格读取`load_p`和`max_renewable_gen_p`，作为对下一时刻的预测值
  * max_renewable_gen_p_all: 106820 * 18
  * load_p_all: 106820 * 91
* reward_type: 'EPRIReward'
* gen_status/steps_to_recorver_gen/steps_to_close_gen: `dim=(54)`，记录发电机状态，由`_update_gen_status`函数更新
* steps_to_reconnect_line/count_soft_overflow_steps: `dim=(185,)`，记录电线状态 
* sample_idx: 一个随机数，代表起始的时刻
* step()
  * 计算`injection_gen_p`和`injection_gen_v`：根据`act`和`last_obs`
  * 随机切断线路，影响电网的结构
  * 运行Power Flow，更新`grid`状态，其中
  * `gen_p`/`gen_q`/`gen_v` 由第一步计算决定
  * `load_p`/`load_q`/`load_v`/`renewable_gen` 根据t从表格读取

### Reward

通过`Enviornment.get_reward(self.obs, last_obs)`计算得到

* line_over_flow_reward * 1
* renewable_consumption_reward * 2
* running_cost_reward * 1: 机组运行费用，归一化后基本上一直是-1
* balanced_gen_reward * 3: 
* gen_reactivate_power_reward * 1
* sub_voltage_reward * 1


### Observation

| 变量命名                     | 数据类型     | DIM  | 含义                                                |
| ---------------------------- | ------------ | ---- | --------------------------------------------------- |
| timestep                     | int          |      | 当前时间步数                                        |
| vTime                        | string       |      | 当前时刻                                            |
| flag                         | int          |      | 各线路潮流收敛情况，1表示不收敛，0表示收敛          |
| grid_loss                    | list[float]  | 1... | *电网损耗（网损值）*                                |
| action_space                 |              |      | 下一时间步的合法动作空间                            |
|                              |              |      |                                                     |
| gen_p                        | list[float]  | 54   | 机组有功出力                                        |
| gen_q                        | list[float]  | 54   | 机组无功出力                                        |
| gen_v                        | list[float]  | 54   | 发电机电压幅值                                      |
| target_dispatch              | list[float]  | 54   | 计算*潮流前*机组有功出力                            |
| actual_dispatch              | list[float]  | 54   | 计算*潮流后*机组有功出力                            |
| gen_status                   | np.ndarray   | 54   | 机组开关机状态，1表示开机，0表示关机                |
| steps_to_recover_gen         | np.ndarray   | 54   | 关机机组允许重启的剩余时间步数，0表示机组是开启状态 |
| steps_to_close_gen           | np.ndarray   | 54   | 重启机组允许关机的剩余时间步数                      |
| unnameindex                  | dict         |      | 机组名称和prodp等的对应关系                         |
|                              |              |      |                                                     |
| curstep_renewable_gen_p_max  | list[float]  | 18   | 当前时间步新能源机组的最大有功出力                  |
| nextstep_renewable_gen_p_max | list[float]  | 18   | 下一时间步新能源机组的最大有功出力                  |
|                              |              |      |                                                     |
| load_p                       | list[float]  | 91   | 负荷有功                                            |
| load_q                       | list[float]  | 91   | 负荷无功                                            |
| load_v                       | list[float]  | 91   | 负荷所在节点电压幅值                                |
| nextstep_load_p              | list[float]  | 91   | 下一时间步的负荷有功                                |
|                              |              |      |                                                     |
| p_or                         | list[float]  | 185  | 支路起始端有功，和线路数相同                        |
| q_or                         | list[float]  | 185  | 支路起始端无功                                      |
| v_or                         | list[float]  | 185  | 支路起始端电压                                      |
| a_or                         | list[float]  | 185  | 支路起始端电流                                      |
| p_ex                         | list[float]  | 185  | 支路末端有功                                        |
| q_ex                         | list[float]  | 185  | 支路末端无功                                        |
| v_ex                         | list[float]  | 185  | 支路末端电压                                        |
| a_ex                         | list[float]  | 185  | 支路末端电流                                        |
| line_status                  | list[bool]   | 185  | 线路状态                                            |
| steps_to_reconnect_line      | np.ndarray   | 185  | 已断开支路恢复连接的剩余时间步数                    |
| count_soft_overflow_steps    | np.ndarray   | 185  | 支路已连续软过载的时间步数                          |
| rho                          | list[float]  | 185  | 支路电流负载率                                      |
|                              |              |      |                                                     |
| busname                      | list[string] | 126  | 各节点名称，共有126个节点                           |
| bus_gen                      | dict         |      | 各节点相连的机组名称                                |
| bus_load                     | dict         |      | 各节点相连的负荷名称                                |
| bus_branch                   | dict         |      | 各节点相连的支路名称                                |
|                              |              |      |                                                     |



### Action

```python
# adjust_gen_p: delta p
# adjust_gen_v: delta v
{"adjust_gen_p": np.ndarray(dtype=np.float32, shape=[54]), "adjust_gen_v": np.ndarray(dtype=np.float32, shape=[54])} 

```

### 向量化Observation
#### 9.4版本
    - gen_p: 54, [-1,1] // dynamic normalized by curtime's max abs value
    - gen_q: 54, [-1,1] // dynamic normalized by curtime's max abs value
    - gen_v: 54, [0,1] // dynamic normalized by curtime's max abs value
    - gen_status: 54, {0,1}
    - steps_to_recover_gen: 54, [0,0.4] // normalized by 100
    - steps_to_close_gen: 54, [0,0.4] // normalized by 100
    - renewable_gen_p_max_diff: 54, [-1,1] // dynamic normalized by curtime's max abs value
    - load_p_diff: 91, [-1,1] // dynamic normalized by curtime's max abs value
    - load_q: 91, [-1,1] // dynamic normalized by curtime's max abs value
    - load_v: 91, [0,1] // dynamic normalized by curtime's max abs value         
Mark: (1) 归一化变量用的是当前时刻的最大值，time dependent (2) 有一些变量用的diff，有一些用的绝对值 (3) 缺少每个bus节点的信息

### 反向量化Action
#### 9.4版本
     - adjust_gen_p: [-0.05, 0.05] // use tanh to squash, then clip by legal_act_space
     - adjust_gen_v: [0.0, 1.0] // use tanh to squash, then clip by legal_act_space
     
#### 9.26版本
     - adjust_gen_p: [-10, 10] // use tanh to squash, then clip by legal_act_space
     - adjust_gen_v: [0,0] // 恒等于0，不控制电压  



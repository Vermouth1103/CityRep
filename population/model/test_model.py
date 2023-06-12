from libcity.config import ConfigParser
from libcity.data import get_dataset
from libcity.utils import get_model, get_executor
from libcity.utils import str2bool, add_general_args, get_logger
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # 增加指定的参数
    parser.add_argument('--task', type=str,
                        default='traffic_state_pred', help='the name of task')
    parser.add_argument('--model', type=str,
                        default='GRU', help='the name of model')
    parser.add_argument('--dataset', type=str,
                        default='METR_LA', help='the name of dataset')
    parser.add_argument('--config_file', type=str,
                        default=None, help='the file name of config file')
    parser.add_argument('--saved_model', type=str2bool,
                        default=True, help='whether save the trained model')
    parser.add_argument('--train', type=str2bool, default=True,
                        help='whether re-train model if the model is trained before')
    parser.add_argument('--exp_id', type=str, default=None, help='id of experiment')
    parser.add_argument('--seed', type=int, default=0, help='random seed')
    parser.add_argument('--cache_model', type=str, default=None, help='cache model')
    # 增加其他可选的参数
    add_general_args(parser)
    # 解析参数
    args = parser.parse_args()
    dict_args = vars(args)
    other_args = {key: val for key, val in dict_args.items() if key not in [
        'task', 'model', 'dataset', 'config_file', 'saved_model', 'train'] and
        val is not None}
    
    '''run_model(task=args.task, model_name=args.model, dataset_name=args.dataset,
              config_file=args.config_file, saved_model=args.saved_model,
              train=args.train, other_args=other_args)'''

    # 加载配置文件
    config = ConfigParser(task=args.task, model=args.model,
                        dataset=args.dataset, config_file=None,
                        other_args={'batch_size': 64, 'exp_id': args.exp_id})
    
    # 如果是交通流量\速度预测任务，请使用下面的加载配置文件语句
    #config = ConfigParser(task='traffic_state_pred', model='TemplateTSP',
        #dataset='Xiongan', config_file=None, other_args={'batch_size': 2})
    #config['exp_id'] = 31941

    # logger
    logger = get_logger(config)
    # 加载数据模块
    dataset = get_dataset(config)
    # 数据预处理，划分数据集
    train_data, valid_data, test_data = dataset.get_data()
    data_feature = dataset.get_data_feature()
    # 抽取一个 batch 的数据进行模型测试
    batch = train_data.__iter__().__next__()

    #model_cache_file = './libcity/cache/50001/model_cache/GRU_Xiongan.m'
    model_cache_file = args.cache_model
    # 加载模型
    model = get_model(config, data_feature)
    executor = get_executor(config, model, data_feature)
    executor.load_model(model_cache_file)
    #executor.load_model_with_epoch(model_cache_file)
    executor.evaluate(train_data)
    #executor.evaluate(valid_data)
    #executor.evaluate(test_data)
    #self = model.to(config['device'])
    # 模型预测
    #batch.to_tensor(config['device'])
    #res = model.predict(batch)
    # 请自行确认 res 的 shape 是否符合赛道的约束
    # 如果要加载执行器的话
    #executor = get_executor(config, model)
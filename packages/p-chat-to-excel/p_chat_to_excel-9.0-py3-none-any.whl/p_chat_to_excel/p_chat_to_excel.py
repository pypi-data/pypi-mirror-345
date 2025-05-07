from openai import OpenAI
import pandas as pd
from tqdm import tqdm
import concurrent.futures
import warnings
warnings.filterwarnings('ignore')
import json

class P_chat_to_excel:
    def __init__(self,
                 api_key ,
                 base_url):
        self.help = '''
*** chat_to_excel 的核心思想（底层逻辑）为：调用通用大模型，针对传入 Excel 文件中的目标字段，依次向大模型发起询问。随后对大模型返回的结果进行解析，将解析后的数据保存至原 Excel 文件中，并对 Excel 格式加以调整，最终将其保存到本地。总的来说，就是先chat，得到结果后(save)to excel。
*** 需注意的点：
1、目前仅支持单个字段的文本分析
2、默认使用Qwen-Plus模型，可更换模型。可选模型列表参考:https://help.aliyun.com/zh/model-studio/getting-started/models。根据任务性质和价格更改！
3、chat_to_excel采用了并行设计，线程为默认值，即根据CPU核心数，综合考虑系统资源来确定一个合适值。虽然核心思想是逐一遍历，但实际是多线程执行，效率较高。
*** 方法介绍：
1、excel_info。传入excel文件的方法。两个参数：path和column。path就是excel文件的本地位置，column就是关键字段，用list形式写入。如有关键字段a和b，则为['a','b']，如果只有a，则为['a']。传入后，可调用df属性（obj.df），获取表格信息。
2、data_parsing。解析通话内容的方法：通话内容来源于datalake_t3_hotline_sgl.dls_t_cc_hotline_record_asr_result中的recog_result字段（sql取出来是什么就是什么，用该方法解析前不要做任何结构上的操作），该字段包括角色、内容、分贝、语速、时间等信息，为了节省资源损耗和时间消耗，可以用该方法保留关键信息，即说话角色和说话内容。且该方法针对开头非人工环节的录音也进行了过滤处理。该方法有一个参数：column，为解析目标字段的名称，即通话内容所在的字段的名称。
3、data_sample。随机抽取出一定行数的数据。因为实际应用场景里，往往数据的量级是很大的，在调整大模型prompt和inquiry的过程中，不可能每次都跑完全部数据来对二者进行调整，这样费时费资源，因此需要随机抽取出n行，先在一小部分数据上调整完毕后，再跑全部数据。只有一个参数：num，即需要抽取多少行的数据。
4、info_collect。简单的交互式信息采集方法。一步步按照提示输入prompt、inquiry、column、result_column_name和file_path信息。信息会存储在环境中。如果需要修改，则需要设置param参数。例如，仅需要修改prompt，其余的不改，则info_collect(param = 'prompt')。如果全部填写，则不需要设置参数，info_collect()即可。
5、chat。核心方法，集chat和to excel为一体。这个参数比较多（但只有一个需要设置，其余不需要，因为大多数都通过info_collect方法收集好了，chat方法会根据info_collect收集到的信息执行）。
需要设置的参数：sample。类型为布尔值，即True或False。True时，仅跑data_sample后随机出来的数据，用来调试prompt和inquiry。False是，则跑全部数据。默认为False。
不需要再次设置的参数：
(1)、prompt。大模型中的prompt，即给大模型立的人设，如果想要通用大模型比较好的应付具体应用场景，这个必填。
(2)、inquiry。询问大模型的话，即聊天框中输入的文字。
(3)、column。目标字段的名字。比如想要大模型分析通话内容，那就需要将excel文件中通话内容所在的那个字段的名称告诉代码，代码才能传参至inquiry中。
(4)、result_column_name。结果字段的名称。大模型传回结果了，代码也临时保存了，这时候就需要写到表格中了，需要给结果命名了。比如分析用户的诉求，那结果字段就可以叫“用户诉求”，代码会创建新的一列字段“用户诉求”并将大模型传入的结果写入。
(5)、file_path。结果保存到本地的地址。后缀为xlsx。
(6)、model。默认为 Qwen-Plus，可修改，可选模型列表参考:https://help.aliyun.com/zh/model-studio/getting-started/models。    
'''
        self.df = None
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key = api_key,
            base_url= base_url,
        )
        self.model = 'qwen-plus'

    def excel_info(self,path,column):
        df = pd.read_excel(path)
        df_filter = df.filter(column)
        self.df = df_filter

    def data_parsing(self,column,truncate_word = '为您服务'):
        list_total = []
        self.df[column] = self.df[column].str.replace('excel单元格限制长度可能有截取：','')
        for x in self.df[column].tolist():
            trigger = False
            try:
                list_context = []
                for i in json.loads(x):
                    if not trigger:
                        if i['text'].find(truncate_word) > -1 and i['text'].find('为了更好') == -1:
                            trigger = True
                            dict_ = {}
                            dict_['role'] = i['role']
                            dict_['text'] = i['text']
                            list_context.append(dict_)
                        else:
                            pass
                    else:
                        dict_ = {}
                        dict_['role'] = i['role']
                        dict_['text'] = i['text']
                        list_context.append(dict_)
                list_total.append(list_context)
            except:
                list_total.append({})
        self.df[column] = list_total
        self.df = self.df[self.df[column] != '[]']
        print('解析完成')

    def concat(self,column):
        for i in column:
            self.df[f'column{i}'] = i + '：' + self.df[i]
        columns_to_combine = self.df.filter(regex='^column').columns
        self.df['combined'] = self.df[columns_to_combine].agg('；'.join, axis=1)
        self.df = self.df.drop(columns=columns_to_combine)

    def data_sample(self,num):
        df_sample = self.df.sample(num)
        self.df_sample = df_sample
        print(f'已随机抽取{num}行，请调用df_sample属性查看')

    def info_collect(self,param = None):
        if param:
            if hasattr(self, param):
                replace = input(f'{param}:')
                setattr(self, param, replace)
            else:
                print(f'类中没有名为 {param} 的属性。')
        else:
            self.prompt = input('prompt（AI的人设）:\n')
            self.inquiry = input('inquiry（询问的内容）：\n')
            self.column = input('column（表格中的目标字段）：\n')
            self.result_column_name = input('result_column_name（结果字段的名称）：\n')
            self.file_path = input('file_path（结果保存到本地的地址）：\n')

    def chat_single(self,sample = False):
        def chat_prepare(i):
            retries = 0
            try:
                result = []
                completion = self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {'role': 'system', 'content': self.prompt},
                        {'role': 'user', 'content': f'这有一段文本：{i}。{self.inquiry}。'}]
                )
                reply = completion.choices[0].message.content
                result.append(reply)
                return result[0]
            except Exception as e:
                while retries < 2:
                    try:
                        retries += 1
                        print(f'出错：{e}，正在进行第{retries}次重试，最大重试次数：2')
                        result = []
                        completion = self.client.chat.completions.create(
                            model= self.model,
                            messages=[
                                {'role': 'system', 'content': self.prompt},
                                {'role': 'user', 'content': f'这有一段文本：{i}。{self.inquiry}。'}]
                        )
                        reply = completion.choices[0].message.content
                        result.append(reply)
                        return result[0]
                        retries = 2
                    except:
                        retries += 1
                        print(f'出错：{e}，正在进行第{retries}次重试，最大重试次数：2')
                        result = []
                        completion = self.client.chat.completions.create(
                            model= self.model,
                            messages=[
                                {'role': 'system', 'content': self.prompt},
                                {'role': 'user', 'content': f'这有一段文本：{i}。{self.inquiry}。'}]
                        )
                        reply = completion.choices[0].message.content
                        result.append(reply)
                        return result[0]
        if not sample:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(tqdm(executor.map(chat_prepare, self.df[self.column]), total=len(self.df[self.column])))
                self.results = results
            self.df[self.result_column_name] = results
            self.df.to_excel(self.file_path,index = False)
            print('done')
        else:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(tqdm(executor.map(chat_prepare, self.df_sample[self.column]), total=len(self.df_sample[self.column])))
                self.results = results
            self.df_sample[self.result_column_name] = results
            self.df_sample.to_excel(self.file_path,index = False)
            print('done')

    def chat_multiple(self,axis = 1,sample = False):
        columns = self.df.columns
        def chat_prepare(i):
            retries = 0
            try:
                result = []
                completion = self.client.chat.completions.create(
                    model= self.model,
                    messages=[
                        {'role': 'system', 'content': self.prompt},
                        {'role': 'user', 'content': f'这有一段文本：{i}。{self.inquiry}。'}]
                )
                reply = completion.choices[0].message.content
                result.append(reply)
                return result[0]
            except Exception as e:
                while retries < 2:
                    try:
                        retries += 1
                        print(f'出错：{e}，正在进行第{retries}次重试，最大重试次数：2')
                        result = []
                        completion = self.client.chat.completions.create(
                            model= self.model,
                            messages=[
                                {'role': 'system', 'content': self.prompt},
                                {'role': 'user', 'content': f'这有一段文本：{i}。{self.inquiry}。'}]
                        )
                        reply = completion.choices[0].message.content
                        result.append(reply)
                        return result[0]
                        retries = 2
                    except:
                        retries += 1
                        print(f'出错：{e}，正在进行第{retries}次重试，最大重试次数：2')
                        result = []
                        completion = self.client.chat.completions.create(
                            model= self.model,
                            messages=[
                                {'role': 'system', 'content': self.prompt},
                                {'role': 'user', 'content': f'这有一段文本：{i}。{self.inquiry}。'}]
                        )
                        reply = completion.choices[0].message.content
                        result.append(reply)
                        return result[0]
        if axis == 1:
            for target_column in tqdm(columns):
                self.target_column = target_column
                if not sample:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        results = list(tqdm(executor.map(chat_prepare, self.df[self.target_column]), total=len(self.df[self.target_column])))
                        self.results = results
                    target_index = self.df.columns.get_loc(target_column)
                    self.df.insert(target_index + 1, f'{target_column}-{self.result_column_name}', results)
                    self.df.to_excel(self.file_path,index = False)
                    print('done')
                else:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        results = list(tqdm(executor.map(chat_prepare, self.df_sample[self.target_column]), total=len(self.df_sample[self.target_column])))
                        self.results = results
                    target_index = self.df_sample.columns.get_loc(target_column)
                    self.df_sample.insert(target_index + 1, f'{target_column}-{self.result_column_name}', results)
                    self.df_sample.to_excel(self.file_path,index = False)
                    print('done')
        else:
            self.results = []
            column_content = []
            for target_column in tqdm(columns):
                self.target_column = target_column
                if not sample:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        results = list(tqdm(executor.map(chat_prepare, self.df[self.target_column]), total=len(self.df[self.target_column])))
                        self.results.extend(results)
                else:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        results = list(tqdm(executor.map(chat_prepare, self.df_sample[self.target_column]), total=len(self.df_sample[self.target_column])))
                        self.results.extend(results)
                column_content.extend([target_column]*len(self.df_sample[self.target_column]))
            pd.DataFrame({'目标内容':column_content,self.result_column_name: self.results}).to_excel(self.file_path,index = False)
            print('done')

    def chat(self,sample=True,axis=None):
        if axis:
            self.chat_multiple(axis = axis,sample = sample)
        else:
            self.chat_single(sample = sample)






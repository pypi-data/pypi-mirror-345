# api_call方法：P_chat_to_excel
*** P_chat_to_excel 的核心思想（底层逻辑）为：调用通用大模型，针对传入 Excel 文件中的目标字段，依次向大模型发起询问。随后对大模型返回的结果进行解析，将解析后的数据保存至原 Excel 文件中，并对 Excel 格式加以调整，最终将其保存到本地。总的来说，就是先chat，得到结果后(save)to excel。

*** 需注意的点：
1、目前仅支持单个字段的文本分析
2、默认使用Qwen-Plus模型，可更换模型。可选模型列表参考:https://help.aliyun.com/zh/model-studio/getting-started/models。根据任务性质和价格更改！
3、P_chat_to_excel采用了并行设计，线程为默认值，即根据CPU核心数，综合考虑系统资源来确定一个合适值。虽然核心思想是逐一遍历，但实际是多线程执行，效率较高。

*** 方法介绍：

1、excel_info。传入excel文件的方法。两个参数：path和column。path就是excel文件的本地位置，column就是关键字段，用list形式写入。如有关键字段a和b，则为['a','b']，如果只有a，则为['a']。传入后，可调用df属性（obj.df），获取表格信息。

2、data_parsing。解析通话内容的方法：通话内容来源于d***_hotline_***.***_hotline_record_***中的recog_result字段（sql取出来是什么就是什么，用该方法解析前不要做任何结构上的操作），该字段包括角色、内容、分贝、语速、时间等信息，为了节省资源损耗和时间消耗，可以用该方法保留关键信息，即说话角色和说话内容。且该方法针对开头非人工环节的录音也进行了过滤处理。该方法有一个参数：column，为解析目标字段的名称，即通话内容所在的字段的名称。

3、concat。字段之间的拼接。通过拼接得以给大模型输入多字段的组合，实现多段分析。

4、data_sample。随机抽取出一定行数的数据。因为实际应用场景里，往往数据的量级是很大的，在调整大模型prompt和inquiry的过程中，不可能每次都跑完全部数据来对二者进行调整，这样费时费资源，因此需要随机抽取出n行，先在一小部分数据上调整完毕后，再跑全部数据。只有一个参数：num，即需要抽取多少行的数据。

5、info_collect。简单的交互式信息采集方法。一步步按照提示输入prompt、inquiry、column、result_column_name和file_path信息。信息会存储在环境中。如果需要修改，则需要设置param参数。例如，仅需要修改prompt，其余的不改，则info_collect(param = 'prompt')。如果全部填写，则不需要设置参数，info_collect()即可。

6、chat。核心方法，集chat和to excel为一体。这个参数比较多（但只有一个需要设置，其余不需要，因为大多数都通过info_collect方法收集好了，chat方法会根据info_collect收集到的信息执行）。
需要设置的参数：sample。类型为布尔值，即True或False。True时，仅跑data_sample后随机出来的数据，用来调试prompt和inquiry。False是，则跑全部数据。默认为False。
不需要再次设置的参数：
  
  (1)、prompt。大模型中的prompt，即给大模型立的人设，如果想要通用大模型比较好的应付具体应用场景，这个必填。
  
  (2)、inquiry。询问大模型的话，即聊天框中输入的文字。
  
  (3)、column。目标字段的名字。比如想要大模型分析通话内容，那就需要将excel文件中通话内容所在的那个字段的名称告诉代码，代码才能传参至inquiry中。
  
  (4)、result_column_name。结果字段的名称。大模型传回结果了，代码也临时保存了，这时候就需要写到表格中了，需要给结果命名了。比如分析用户的诉求，那结果字段就可以叫“用户诉求”，代码会创建新的一列字段“用户诉求”并将大模型传入的结果写入。
  
  (5)、file_path。结果保存到本地的地址。后缀为xlsx。
  
  (6)、model。默认为 Qwen-Plus，可修改，可选模型列表参考:https://help.aliyun.com/zh/model-studio/getting-started/models。   

# 作者: 徐鹏
# 邮箱: xupeng23456@126.com
# 创建日期: 2025年4月24日

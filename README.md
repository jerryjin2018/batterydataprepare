### 介绍
客户提供的关于车电池的数据，是按照车的VIN号和收集的时间存放在很多个CSV文件中。为了之后PoC过程中观察和理解数据。所以需要做如下几件事:  
````
1. 按照车辆的VIN后将所有的CSV文件存放到不同的S3的子目录中，子目录以VIN号命名
2. 对存放于同一个子目录中的所有CSV文件进行合并
3. 观察合并后的文件，并除去那些空行的数据
4. 将处理后的数据，选取需要的字段，重新保存到S3中VIN号命名子目录的final目录中
````
### 步骤  
1） 1.migrate_group_files.py 主要就是将形如 ADCDDBAA0KP0001_20200101170000.CSV（文件名:VIN号_日期和时间.CSV) 格式的文件文件存放到对于的VIN号的S3的子目录（ADCDDBAA0KP0001）中。

2） 2.rmsdataprocessing.ipynb 是pyspark脚本用来合并，处理异常数据，已经最终输出需要的数据。其具体内容:  

i) 创建EMR集群为了跑PySpark，注意创建时选上 Name=JupyterEnterpriseGateway, Name=Spark, Name=Livy; 可以参考如下创建的EMR的命令
```
aws emr create-cluster --termination-protected --applications Name=Hadoop Name=JupyterEnterpriseGateway Name=Spark Name=Livy --ec2-attributes '{"KeyName":"key-*****-new","InstanceProfile":"EMR_EC2_DefaultRole","SubnetId":"subnet-08e5c1c41981c****","EmrManagedSlaveSecurityGroup":"sg-0d5296d5ecc31****","EmrManagedMasterSecurityGroup":"sg-0f5a587aa2c9d****"}' --release-label emr-5.33.0 --log-uri 's3n://aws-logs-*****-cn-northwest-1/elasticmapreduce/' --instance-groups '[{"InstanceCount":2,"EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"SizeInGB":32,"VolumeType":"gp2"},"VolumesPerInstance":2}]},"InstanceGroupType":"CORE","InstanceType":"m5.xlarge","Name":"Core - 2"},{"InstanceCount":1,"EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"SizeInGB":32,"VolumeType":"gp2"},"VolumesPerInstance":2}]},"InstanceGroupType":"MASTER","InstanceType":"m5.xlarge","Name":"Master - 1"}]' --configurations '[{"Classification":"spark-hive-site","Properties":{"hive.metastore.client.factory.class":"com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"}}]' --auto-scaling-role EMR_AutoScaling_DefaultRole --ebs-root-volume-size 30 --service-role EMR_DefaultRole --enable-debugging --name 'pysparktest4' --scale-down-behavior TERMINATE_AT_TASK_COMPLETION --region cn-northwest-1
```

ii)  为了更好的探索和观赏数据，我这里使用的Jupyter notebook，EMR选项中直接创建，并连接刚创建好的EMR集群。

iii) 打开创建好的JupyterLab，将 2.rmsdataprocessing.ipynb 文件上传到环境中。因为使用的是PySpark，这里kernel就选择PySpark。此脚本完成了将同一个VIN号的目录最终多个CSV文件进行合并，除去空行，因为文件本来的字段有86个，我们只需要保留需要的字段，将最终将处理好的数据再保存到S3中VIN号命名子目录的final目录中。

### 特别注意
````
1.客户提供的数据的字符集为GB2312/GBk,而PySpark默认是UTF8，所以在使用PySpark的DataFrame读取数据时需要指定字符编码。 
2.将多个CSV文件合并后，表头只保留了一个，同时保存的文件的字符集也变成了UTF8
3.因为PySpark的DataFrame的内置函数还是Spark SQL都无法很好的处理中文的表头（非中文的内容），所以需要创建对应英文的schema来处理数据。
````




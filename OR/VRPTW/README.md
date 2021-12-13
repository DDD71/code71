# VRPTW
The Vehicle Routing Problem with Time Windows (VRPTW) is the extension of the Capacitated Vehicle Routing Problem (CVRP) where the service at each customer must start within an associated time interval, called a time window. Time windows may be hard or soft. In case of hard time windows, a vehicle that arrives too early at a customer must wait until the customer is ready to begin service. In general, waiting before the start of a time window incurs no cost. In the case of soft time windows, every time window can be violated barring a penalty cost. The time windows may be one-sided, e.g., stated as the latest time for delivery.

## model

The VRPTW can be formulated as the following multi-commodity network flow model with time-window and capacity constraints:
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210410162330452.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0RDWFk3MQ==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210410163058871.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0RDWFk3MQ==,size_16,color_FFFFFF,t_70)





## Numerical example
'R101.txt' is from solomon benchmark, more details can be found in [solomon-benchmark](https://www.sintef.no/projectweb/top/vrptw/solomon-benchmark/).

1. Team: Kaiwen Qi, Hao Huang
2. The hardest part was implementing how to update the corresponding distance in a RoutingUpdate packet. Also, we spent a lot of time understanding the whole project structure.
3. Packet queuing.
4. We can handle link weights, but not incremental updates.Each link weight update is triggered by Discovery Packet. Then we compare their before and after distance vectors; if there’s a difference, we will send routing update. However, this might make us sending too many routing updates.
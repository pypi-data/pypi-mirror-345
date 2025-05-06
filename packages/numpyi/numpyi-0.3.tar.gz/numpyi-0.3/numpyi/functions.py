def dc1():
    code = '''
#server.py
from xmlrpc.server import SimpleXMLRPCServer
import threading

def factorial(n):
    if n==0 or n==1:
        return 1
    else:
        return n*factorial(n-1)
    
def shutdown():
    print("Shutting down server...")
    threading.Thread(target=server.shutdown).start()
    return "Server shut down."

server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
print("Server is listening on port 8000")
server.register_function(factorial, "factorial")
server.register_function(shutdown, "shutdown")
server.serve_forever()

**************************************************************
#client.py
from xmlrpc.client import ServerProxy

proxy = ServerProxy("http://localhost:8000/")

while True:
    user_input = input("Enter a number to compute it's factorial (or type 'exit' to close)").strip()

    if user_input.lower() == 'exit':
        try:
            print(proxy.shutdown())
        except:
            print("Server is already shut")
        break

    try:
        num = int(user_input)
        result = proxy.factorial(num)
        print(f"Factorial of {num} is {result}")
    except ValueError:
        print("Enter a valid number")
'''
    return code

def dc2():
    code = '''
#ConcatService.java

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface ConcatService extends Remote {
    String concatenate(String str1, String str2) throws RemoteException;
}

*******************************************************************************
#ConcatServer.java

import java.rmi.Naming;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class ConcatServer extends UnicastRemoteObject implements ConcatService {
    protected ConcatServer() throws RemoteException {
        super();
    }

    @Override
    public String concatenate(String str1, String str2) throws RemoteException {
        return str1 + str2;
    }

    public static void main(String[] args) {
        try {
            ConcatServer server = new ConcatServer();
            Naming.rebind("rmi://localhost/ConcatService", server);
            System.out.println("Server is running...");
        } catch (Exception e) {
            System.err.println("Server exception: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
************************************************************************************
#ConcatClient.java

import java.rmi.Naming;
import java.util.Scanner;

public class ConcatClient {
    public static void main(String[] args) {
        try {
            ConcatService service = (ConcatService) Naming.lookup("rmi://localhost/ConcatService");
            Scanner scanner = new Scanner(System.in);
            
            while (true) {
                System.out.println("Menu:");
                System.out.println("1. Concatenate Strings");
                System.out.println("2. Exit");
                System.out.print("Enter choice: ");
                
                int choice = scanner.nextInt();
                scanner.nextLine(); // Consume newline
                
                if (choice == 1) {
                    System.out.print("Enter first string: ");
                    String str1 = scanner.nextLine();
                    
                    System.out.print("Enter second string: ");
                    String str2 = scanner.nextLine();
                    
                    String result = service.concatenate(str1, str2);
                    System.out.println("Concatenated Result: " + result);
                } else if (choice == 2) {
                    System.out.println("Exiting...");
                    break;
                } else {
                    System.out.println("Invalid choice. Please try again.");
                }
            }
            
            scanner.close();
        } catch (Exception e) {
            System.err.println("Client exception: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

'''
    return code

def dc3():
    code = '''
a) Character counting in a given text file

1. su hduser
   cd

2. nano word_count.txt

3. start-dfs.sh
   start-yarn.sh
   jps

4. hdfs dfs -ls /
   hdfs dfs -rm -r /input
   hdfs dfs -mkdir -p /input
   hdfs dfs -put word_count.txt /input/

5. whereis hadoop
   hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar wordcount /input /output

6. hdfs dfs -ls /output/
   hdfs dfs -cat /output/part-r-00000

*************************************************************************************************************************

b) Counting no. of occurrences of every word in a given text file.

1. su hduser
   cd

2. start-dfs.sh
   start-yarn.sh
   jps

3. hdfs dfs -mkdir -p /input
   hdfs dfs -ls /

4. nano character_count.txt

5. hdfs dfs -put character_count.txt /input/

6. nano mapper.py
    #!/usr/bin/env python3
    import sys
    for line in sys.stdin:
        for char in line.strip():
            print(f"{char}\t1")

   nano reducer.py
    #!/usr/bin/env python3
    import sys
    from collections import defaultdict
    counts = defaultdict(int)
    for line in sys.stdin:
        key, val = line.strip().split("\t")
        counts[key] += int(val)
    for key in sorted(counts):
        print(f"{key}\t{counts[key]}")

   chmod +x mapper.py
   chmod +x reducer.py

7. whereis hadoop
   hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.4.jar \
   > -input /input/character_count.txt \
   > -output /output/character_output \
   > -mapper mapper.py \
   > -reducer reducer.py \
   > -file mapper.py \
   > -file reducer.py

8. hdfs dfs -ls /output/character_output/
   hdfs dfs -cat /output/character_output/part-00000

'''
    return code

def dc4():
    code = '''
    import time
import random

class RoundRobin:
    def __init__(self, servers):
        self.servers = servers
        self.current_index = -1
    
    def get_next_server(self):
        self.current_index = (self.current_index + 1) % len(self.servers)
        return self.servers[self.current_index]


class WeightedRoundRobin:
    def __init__(self, servers, weights):
        self.servers = servers
        self.weights = weights
        self.current_index = -1
        self.current_weight = 0
    
    def get_next_server(self):
        while True:
            self.current_index = (self.current_index + 1) % len(self.servers)
            if self.current_index == 0:
                self.current_weight -= 1
                if self.current_weight <= 0:
                    self.current_weight = max(self.weights)
            if self.weights[self.current_index] >= self.current_weight:
                return self.servers[self.current_index]


class LeastConnections:
    def __init__(self, servers):
        self.servers = {server: 0 for server in servers}
    
    def get_next_server(self):
        # Find the minimum number of connections
        min_connections = min(self.servers.values())
        # Get all servers with the minimum number of connections
        least_loaded_servers = [server for server, connections in self.servers.items() if connections == min_connections]
        # Select a random server from the least loaded servers
        selected_server = random.choice(least_loaded_servers)
        self.servers[selected_server] += 1
        return selected_server
    
    def release_connection(self, server):
        if self.servers[server] > 0:
            self.servers[server] -= 1


class LeastResponseTime:
    def __init__(self, servers):
        self.servers = servers
        self.response_times = [0] * len(servers)
    
    def get_next_server(self):
        min_response_time = min(self.response_times)
        min_index = self.response_times.index(min_response_time)
        return self.servers[min_index]
    
    def update_response_time(self, server, response_time):
        index = self.servers.index(server)
        self.response_times[index] = response_time

def simulate_response_time():
    # Simulating response time with random delay
    delay = random.uniform(0.1, 1.0)
    time.sleep(delay)
    return delay

def demonstrate_algorithm(algorithm_name, load_balancer, iterations=6, use_response_time=False, use_connections=False):
    print(f"\n---- {algorithm_name} ----")
    
    for i in range(iterations):
        server = load_balancer.get_next_server()
        print(f"Request {i + 1} -> {server}")
        
        if use_response_time:
            response_time = simulate_response_time()
            load_balancer.update_response_time(server, response_time)
            print(f"Response Time: {response_time:.2f}s")
        
        if use_connections:
            load_balancer.release_connection(server)


if __name__ == "__main__":
    servers = ["Server1", "Server2", "Server3"]
    
    # Round Robin
    rr = RoundRobin(servers)
    demonstrate_algorithm("Round Robin", rr)
    
    # Weighted Round Robin
    weights = [5, 1, 1]  
    wrr = WeightedRoundRobin(servers, weights)
    demonstrate_algorithm("Weighted Round Robin", wrr, iterations=7)
    
    # Least Connections
    lc = LeastConnections(servers)
    demonstrate_algorithm("Least Connections", lc, use_connections=True)
    
    # Least Response Time
    lrt = LeastResponseTime(servers)
    demonstrate_algorithm("Least Response Time", lrt, use_response_time=True)
'''
    return code

def dc5():
    code = '''
1. su hduser
   cd

2. start-dfs.sh
   start-yarn.sh
   jps

3. hdfs dfs -mkdir -p /input
   hdfs dfs -ls /

4. nano weather_data.txt

5. hdfs dfs -put weather_data.txt /input/

6. nano mapper.py
    #!/usr/bin/env python3
    import sys

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split()
        if len(parts) == 3:
            date_str, min_temp, max_temp = parts
            if "-" in date_str:
                year = date_str.split("-")[0]
                print(f"{year} {min_temp} {max_temp}")


   nano reducer.py
    #!/usr/bin/env python3
    import sys
    from collections import defaultdict

    temps_by_year = defaultdict(list)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 3:
            continue
        year, min_temp, max_temp = parts
        try:
            temps_by_year[year].append((int(min_temp), int(max_temp)))
        except:
            continue

    for year in sorted(temps_by_year.keys()):
        mins, maxs = zip(*temps_by_year[year])
        print(f"{year}\t{min(mins)}\t{max(maxs)}")


   chmod +x mapper.py
   chmod +x reducer.py

7. whereis hadoop
   hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.4.jar \
   > -input /input/weather_data.txt \
   > -output /output/weather_output \
   > -mapper mapper.py \
   > -reducer reducer.py \
   > -file mapper.py \
   > -file reducer.py

8. hdfs dfs -ls /output/weather_output/
   hdfs dfs -cat /output/weather_output/part-00000
'''
    return code
# **TCC**

## **Ryu Controller**

> `ryu-manager controller.py`

---

## **Mininet Topo**

2 switches with 2 hosts each

> `sudo python3 topo.py`

### **Ping Test**

> `host1 ping [opts] host2`
>
> **opts:**
>
> **-c** number of packages
>
> **-s** length of packages
>
> **-f** create a 10ms interval between packages

---

## Datasets

### Test Dataset

https://www.unb.ca/cic/datasets/ids-2017.html

day: monday

data status: benign

---

## Install

### VSCode

> sudo snap install --classic code

### Mininet

> git clone git://github.com/mininet/mininet

> mininet/util/install.sh -a

### Ryu-manager

> pip install ryu

### Scapy

> pip install scapy

---

### **Bug Fix eventlet**

Eventlet with some problems at newest version until today (01/08/2022), use 0.30.2 instead.

> `pip install eventlet==0.30.2`

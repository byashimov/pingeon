# Pingeon

[![Build Status](https://travis-ci.org/byashimov/pingeon.svg?branch=master)](https://travis-ci.org/byashimov/pingeon)
[![codecov](https://codecov.io/gh/byashimov/pingeon/branch/master/graph/badge.svg)](https://codecov.io/gh/byashimov/pingeon) 

A pinging project.

```bash
                             __,---,
               .---.        /__|o\  )       .-"-.      .----.""".
              /   6_6        `-\ / /       / 4 4 \    /____/ (0 )\
              \_  (__\         ,) (,       \_ v _/      `--\_    /
              //   \\         //   \\      //   \\         //   \\
             ((     ))       {(     )}    ((     ))       {{     }}
       =======""===""=========""===""======""===""=========""===""=======
       jgs      |||            |||||         |||             |||
                 |              |||           |              '|'
```

ASCII [Copyright](https://www.oocities.org/spunk1111/birds.htm)


## Installation

todo: put some instructions here.

```bash
$ pip install -e git://github.com/byashimov/pingeon.git#egg=pingeon
```

## Project architecture

Most interfaces are just `func()` calls,
so components are not tied up and can be replaced any time.

```bash                                        
                                                                     
 1. Consumer                                                        
 ===========                                                        
                                                                    
 +---------------+        +--------------+       +-----------------+
 |               | func() |              |       |                 |
 |  Regular job  | -----> |   Producer   | ----> |  Kafka producer |
 |               |        |              |       |                 |
 +---------------+        +--------------+       +-----------------+
                                 ^                                  
                                 |  func()                          
                          +--------------+                          
                          |   +--------+ |   Create logs            
                          |   | check  | |   with unique UUID       
                          |   +--------+ |                          
                          |              |                          
                          |   +-------+  |                          
                          |   | check |  |                          
                          |   +-------+  |                          
                          +--------------+                          
                                                                    
                                   ---------------------------------
 ---------------------------------/                                 
                                                                    
 2. Producer                                                        
 ===========                                                        
                                                                    
 +---------------+        +--------------+       +-----------------+
 |               | func() |              |       |                 |
 |  Regular job  | -----> |   Consumer   | <---- |  Kafka consumer |
 |               |        |              |       |                 |
 +---------------+        +--------------+       +-----------------+
                                 |                                  
                                 V                                  
                         +-----------------+                        
     INSERT              |                 |                        
     ON CONFLICT UUID    |    Postgres     |                        
     DO NOTHING          |     Client      |                        
     PARTITION BY RANGE  |                 |                        
                         +-----------------+                        
```

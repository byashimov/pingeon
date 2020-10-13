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

```bash
$ pip install -e git://github.com/byashimov/pingeon.git#egg=pingeon
```

## Project architecture

```bash                                        
                                                                     
 1. Producer                                                        
 ===========                                                        
                                                                    
 +---------------+        +--------------+       +-----------------+
 |               | func() |              | Log   |                 |
 |  Regular job  | -----> |   Producer   | ----> |  Kafka producer |
 |               |        |              |       |                 |
 +---------------+        +--------------+       +-----------------+
                                 ^                                  
                                 | func() -> dict                     
                          +-------------+                          
                          |  +-------+  |   Create Log            
                          |  | check |  |   with unique Log.uid       
                          |  +-------+  |                          
                          |             |                          
                          |  +-------+  |                          
                          |  | check |  |                          
                          |  +-------+  |                          
                          +-------------+                          
                                                                    
                                   ---------------------------------
 ---------------------------------/                                 
                                                                    
 2. Consumer                                                        
 ===========                                                        
                                                                    
 +---------------+        +--------------+       +-----------------+
 |               | func() |              | Log   |                 |
 |  Regular job  | -----> |   Consumer   | <---- |  Kafka consumer |
 |               |        |              |       |                 |
 +---------------+        +--------------+       +-----------------+
                                 | Log                              
                                 V                                  
                         +-----------------+                        
     INSERT              |                 |                        
     ON CONFLICT UID     |    Postgres     |                        
     DO NOTHING          |     client      |                        
     PARTITION BY RANGE  |                 |                        
                         +-----------------+                        
```

Project contains several components:

1. A regular job `worker`. Runs given `func` every given `interval` in seconds
1. `producer` which run any amount of `checkers` 
   and save those result as a labeled `Log` with an unique uid to Kafka
1. "Checkers" are just regular functions      
1. `consumer` is also run by `worker`, reads Kafka topic 
   and saves data to partitioned table in Postgres.
   Since Kafka guarantees at least on delivery it doesn't fail with existing log uid. 

Every component is well isolated by simple interfaces:

- `worker` run any async function
- `producer` run any async function, which however must return a dictionary
- `checker` does whatever it does until it returns a dictionary
- both `consumer` and `producer` use "repositories" to read or save data.
  All of them use `Log` object as a contract.

See `tests/test_integration.py` for usage example.

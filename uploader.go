package main

import (
    "log"
)

const (
	workerCount = 10
)

var (
	pool          WorkerPool
	currentWorker = 0
)

type Uploadable interface {
	Upload() error
}

type Worker struct {
	Id    int
    Done  chan bool
	Tasks chan Uploadable
}

type WorkerPool []*Worker

func (w *Worker) Start() {
	for {
		n := <-w.Tasks

        err := n.Upload()
        if err != nil {
            log.Printf("Error: %s\n", err.Error())
            w.Done <- false
        } else {
            w.Done <- true
        }
	}
}

func AddUploadable(n Uploadable) {
	pool[currentWorker].Tasks <- n

	currentWorker++
	if currentWorker == workerCount {
		currentWorker = 0
	}
}

func initWorkers() {
	pool = make(WorkerPool, workerCount)

	for i := 0; i < workerCount; i++ {
		pool[i] = new(Worker)
		pool[i].Tasks = make(chan Uploadable)
        pool[i].Done = uploads
		pool[i].Id = i

		go pool[i].Start()
	}
}

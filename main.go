package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"github.com/cheggaaa/pb"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"strings"
)

var (
	config  Config
	uploads chan bool
)

type Config struct {
	Ftp struct {
		User     string `json:"user"`
		Password string `json:"pass"`
		Server   string `json:"server"`
		Port     int    `json:"port"`
	} `json:"ftp"`

	Overviewer struct {
		Location   string `json:"location"`
		Configfile string `json:"config"`
		Outputdir  string `json:"outdir"`
		Changelist string `json:"changelist"`
	} `json:"overviewer"`

	Gs struct {
		Bucket string `json:"bucket"`
		client *http.Client
	} `json:"gs"`

	SkipFtp      bool `json:"skip_ftp"`
	SkipGenerate bool `json:"skip_generate"`
	SkipPoi      bool `json:"skip_poi"`
	SkipS3       bool `json:"skip_s3"`
	SkipGs       bool `json:"skip_gs"`
}

func runOverviewer() error {
	script := fmt.Sprintf("%soverviewer.py", config.Overviewer.Location)
	configfile := fmt.Sprintf("--config=%s", config.Overviewer.Configfile)

	cmd := exec.Command("python", script, configfile)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	if err != nil {
		return err
	}

	return cmd.Wait()
}

func sanitizePath(filename string) string {
	od := config.Overviewer.Outputdir
	return fmt.Sprintf("%s%s", od, strings.Split(filename, od)[1])
}

func uploadStatic() error {
	staticFiles := []string{
		"backbone.js",
		"baseMarkers.js",
		"bed.png",
		"compass_lower-left.png",
		"compass_lower-right.png",
		"compass_upper-left.png",
		"compass_upper-right.png",
		"control-bg-active.png",
		"control-bg.png",
		"index.html",
		"markers.js",
		"markersDB.js",
		"index.html",
		"overviewer.css",
		"overviewer.js",
		"overviewerConfig.js",
		"regions.js",
		"signpost_icon.png",
		"signpost-shadow.png",
		"signpost.png",
		"underscore.js",
	}

	filelist := make([]string, len(staticFiles))
	for i, v := range staticFiles {
		filelist[i] = config.Overviewer.Outputdir + "/" + v
	}

	doUpload(filelist)

	return nil
}

func uploadTiles() error {
	f, err := os.Open(config.Overviewer.Changelist)
	if err != nil {
		return err
	}
	defer f.Close()

	var filelist []string
	lines := bufio.NewReader(f)

	for err == nil {
		filename, _, err := lines.ReadLine()

		if err == nil {
			filelist = append(filelist, sanitizePath(string(filename)))
		} else {
			break
		}
	}

	doUpload(filelist)

	return nil
}

func doUpload(filelist []string) {
	length := len(filelist)

	pb.BarStart = "["
	pb.BarEnd = "]"
	pb.Empty = " "
	pb.Current = "#"
	pb.CurrentN = ">"

	bar := pb.StartNew(length)

	var total int

	index := 0
loop:
	for {
		select {
		case <-uploads:
			total = total + 1
			bar.Increment()

			if total == length {
				break loop
			}
		default:
			if index < length {
				uploadFile(filelist[index])
				index++
			}
		}
	}
}

func uploadFile(filename string) {
	file, err := ioutil.ReadFile(filename)
	if err != nil {
		log.Fatalf("error opening %q: %v", filename, err)
	}

	AddUploadable(&GsUpload{
		path:   strings.Split(filename, config.Overviewer.Outputdir+"/")[1],
		bucket: config.Gs.Bucket,
		object: file,
	})
}

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())

	uploads = make(chan bool, 10)

	body, err := ioutil.ReadFile("config.json")
	if err != nil {
		panic(err.Error())
	}

	err = json.Unmarshal(body, &config)
	if err != nil {
		panic(err.Error())
	}

	if !config.SkipGenerate {
		err = runOverviewer()
		if err != nil {
			log.Fatal(err.Error())
		}
	}

	if !config.SkipGs {
		initWorkers()

		c := NewOauthClient("https://www.googleapis.com/auth/devstorage.read_write")
		config.Gs.client = c

		fmt.Println("Uploading tiles...")
		err = uploadTiles()
		if err != nil {
			log.Fatal(err.Error())
		}

		fmt.Println("Uploading static files...")
		err = uploadStatic()
		if err != nil {
			log.Fatal(err.Error())
		}
	}
}

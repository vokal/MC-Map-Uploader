package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"github.com/cheggaaa/pb"
	"github.com/jlaffaye/goftp"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"strings"
)

const (
	WorldZip = "world.zip"
)

var (
	config Config
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

	S3 struct {
		Key    string `json:"key"`
		Secret string `json:"secret"`
		Bucket string `json:"bucket"`
	} `json:"s3"`

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

func runOverviewer(params ...string) error {
	cmd := exec.Command("python", params...)
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

	if length == 0 {
		fmt.Println("No new tiles to upload")
		return
	}

	pb.BarStart = "["
	pb.BarEnd = "]"
	pb.Empty = " "
	pb.Current = "#"
	pb.CurrentN = ">"

	bar := pb.StartNew(length)

	c := initWorkers()
	go func() {
		for i := 0; i < length; i++ {
			uploadFile(filelist[i])
		}
	}()

	var total int
	for total < length {
		select {
		case <-c:
			total = total + 1
			bar.Increment()
		}
	}

	bar.Finish()
}

func uploadFile(filename string) {
	file, err := ioutil.ReadFile(filename)
	if err != nil {
		log.Fatalf("error opening %q: %v", filename, err)
	}

	if !config.SkipGs && config.Gs.Bucket != "" {
		AddUploadable(&GsUpload{
			path:   strings.Split(filename, config.Overviewer.Outputdir+"/")[1],
			bucket: config.Gs.Bucket,
			object: file,
		})
	}

	if !config.SkipS3 && config.S3.Bucket != "" {
		AddUploadable(&S3Upload{
			accessKey: config.S3.Key,
			secretKey: config.S3.Secret,
			path:      strings.Split(filename, config.Overviewer.Outputdir+"/")[1],
			bucket:    config.S3.Bucket,
			object:    file,
		})
	}
}

func doUploads() {
	fmt.Println("Uploading tiles...")
	err := uploadTiles()
	if err != nil {
		log.Fatal(err.Error())
	}
}

func unzipBackup() error {
	cmd := exec.Command("unzip", WorldZip)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Start()
	if err != nil {
		return err
	}

	return cmd.Wait()
}

func handleFtp() error {
	conn, err := ftp.Connect(fmt.Sprintf("%s:%d", config.Ftp.Server, config.Ftp.Port))
	if err != nil {
		return err
	}
	defer conn.Quit()

	err = conn.Login(config.Ftp.User, config.Ftp.Password)
	if err != nil {
		return err
	}

	src, err := conn.Retr(WorldZip)
	if err != nil {
		return err
	}

	dest, err := os.Create(WorldZip)
	if err != nil {
		return err
	}

	fmt.Println("Downloading world.zip...")
	buf := bufio.NewWriter(dest)
	buf.ReadFrom(src)
	buf.Flush()
	fmt.Println("Download complete")

	fmt.Println("Unpacking world.zip...")
	unzipBackup()

	return nil
}

func handleGenerate() error {
	script := fmt.Sprintf("%soverviewer.py", config.Overviewer.Location)
	configfile := fmt.Sprintf("--config=%s", config.Overviewer.Configfile)

	err := runOverviewer(script, configfile)
	if err != nil {
		return err
	}

	poi := "--genpoi"
	return runOverviewer(script, configfile, poi)
}

func handleUpload() error {
	fmt.Println("Uploading tiles...")
	err := uploadTiles()
	if err != nil {
		return err
	}

	fmt.Println("Uploading static files...")
	return uploadStatic()
}

func init() {
	runtime.GOMAXPROCS(runtime.NumCPU())

	body, err := ioutil.ReadFile("config.json")
	if err != nil {
		panic(err.Error())
	}

	err = json.Unmarshal(body, &config)
	if err != nil {
		panic(err.Error())
	}
}

func main() {
	if !config.SkipFtp {
		err := handleFtp()
		if err != nil {
			log.Fatal(err.Error())
		}
	}

	if !config.SkipGenerate {
		err := handleGenerate()
		if err != nil {
			log.Fatal(err.Error())
		}
	}

	if !config.SkipGs && config.Gs.Bucket != "" {
		c := NewOauthClient("https://www.googleapis.com/auth/devstorage.read_write")
		config.Gs.client = c
	}

	if !config.SkipGs || !config.SkipS3 {
		err := handleUpload()
		if err != nil {
			log.Fatal(err.Error())
		}
	}
}

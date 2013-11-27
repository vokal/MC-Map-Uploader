package main

import (
	"bytes"
	"fmt"
	"github.com/kr/s3"
	"net/http"
	"strings"
	"time"
)

type S3Upload struct {
	accessKey string
	secretKey string
	path      string
	bucket    string
	object    []byte
}

func (g *S3Upload) getMimetype(filename string) string {
	extension := strings.Split(filename, ".")[1]

	switch extension {
	case "jpg":
		return "image/jpeg"
	case "png":
		return "image/png"
	case "gif":
		return "image/gif"
	case "html":
		return "text/html"
	case "css":
		return "text/css"
	case "js":
		return "text/javascript"
	}

	return "text/plain"
}

func (g *S3Upload) Upload() error {
	keys := s3.Keys{
		AccessKey: g.accessKey,
		SecretKey: g.secretKey,
	}
	urls := fmt.Sprintf("http://%s.s3.amazonaws.com/%s", g.bucket, g.path)

	body := bytes.NewReader(g.object)
	req, _ := http.NewRequest("PUT", urls, body)

	req.ContentLength = int64(body.Len())
	req.Header.Set("Date", time.Now().UTC().Format(http.TimeFormat))
	req.Header.Set("X-Amz-Acl", "public-read")
	req.Header.Set("Content-Type", g.getMimetype(g.path))
	s3.Sign(req, keys)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	return nil
}

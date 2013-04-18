package main

import (
	"bytes"
	"fmt"
	"github.com/kr/s3"
	"net/http"
	"net/url"
	"time"
)

type S3Upload struct {
	accessKey string
	secretKey string
	path      string
	bucket    string
	object    []byte
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
	s3.Sign(req, keys)
	fmt.Println(req)

	proxyUrl, err := url.Parse("http://localhost:8888")
	myClient := &http.Client{Transport: &http.Transport{Proxy: http.ProxyURL(proxyUrl)}}
	resp, err := myClient.Do(req)
	fmt.Println("S3 Upload", g.path, urls)
	fmt.Println(resp)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	return nil
}

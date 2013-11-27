package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
)

type GsUpload struct {
	path   string
	bucket string
	object []byte
}

func (g *GsUpload) getMimetype(filename string) string {
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

func (g *GsUpload) Upload() error {
	urls := fmt.Sprintf("http://storage.googleapis.com/%s/%s", g.bucket, g.path)
	params := make(url.Values)

	urls += "?" + params.Encode()

	req, _ := http.NewRequest("PUT", urls, nil)

	req.Header.Set("User-Agent", "google-api-go-client/0.5")
	req.Header.Set("Content-Type", g.getMimetype(g.path))
	req.Header.Set("x-goog-project-id", "531339420526")

	body := ioutil.NopCloser(bytes.NewReader(g.object))
	req.Body = body
	req.ContentLength = int64(len(g.object))

	resp, err := config.Gs.client.Do(req)
	if err != nil {
		return err
	}

	defer resp.Body.Close()

	return nil
}

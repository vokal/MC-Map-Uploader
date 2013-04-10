package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
)

type GsUpload struct {
	path   string
	bucket string
	object []byte
}

func (g *GsUpload) Upload() error {
	urls := fmt.Sprintf("http://storage.googleapis.com/%s/%s", g.bucket, g.path)
	params := make(url.Values)

	urls += "?" + params.Encode()

	req, _ := http.NewRequest("PUT", urls, nil)

	req.Header.Set("User-Agent", "google-api-go-client/0.5")
	req.Header.Set("Content-Type", "text/plain")
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

package main

import (
	"fmt"
	"math/rand"
	"net/http"
	"testing"

	"github.com/mgutz/ansi"
)

func TestValidOnionURL(t *testing.T) {
	table := []struct {
		url string
		ans bool
	}{
		{"https://www.google.com", false},
		{"https://www.facebook.com", false},
		{"http://torlinkbgs6aabns.onion/", true},
		{"https://www.propub3r6espa33w.onion", true},
		{"asfasf", false},
		{"www.twitter.com", false},
		{"www.facebookcorewwi.onion", false},
		{"ftp://asfasdf.lkjkl", false},
	}

	for _, testData := range table {
		if testData.ans != validOnionURL(testData.url) {
			t.Errorf("%v received the value %v for being a valid onion url.",
				testData.url,
				validOnionURL(testData.url))
		}
	}
}

type mockClient struct {
	mockResponse map[string]*http.Response
	Error        error
}

func (client mockClient) Head(url string) (*http.Response, error) {
	return client.mockResponse[url], client.Error
}

func TestCheckURL(t *testing.T) {
	ch := make(chan string)
	red := ansi.ColorFunc("red")
	var err error

	for i := 0; i < 10; i++ {
		stCode := rand.Intn(600)
		if stCode > 400 {
			err = http.ErrNoLocation
		} else {
			err = nil
		}
		client := mockClient{map[string]*http.Response{"url": &http.Response{StatusCode: stCode}}, err}
		go checkURL(client, "url", ch)
		res := <-ch

		switch {
		case stCode <= 400:
			desiredRes := fmt.Sprint("url is reachable.\n")
			if res != desiredRes {
				t.Errorf("Status Code of %v returned %v", stCode, res)
			}
		default:
			desiredRes := red(fmt.Sprint("url is not reachable.\n"))
			if res != desiredRes {
				t.Errorf("Status Code of %v returned %v", stCode, res)
			}
		}
	}
}

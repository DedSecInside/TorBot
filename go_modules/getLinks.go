package main

import "C"

import (
	"fmt"
	"golang.org/x/net/html"
	"log"
	"net/http"
	"net/url"
	"sync"
	"time"
)

func asyncHead(client *http.Client, link string) {
	defer wg.Done()
	resp, err := client.Get(link)
	if err == nil && resp.StatusCode < 400 {
		fmt.Printf("%v is reachable.\n", link)
	} else {
		fmt.Printf("%v is not reachable.\n", link)
	}
}

var wg sync.WaitGroup

//export GetLinks
func GetLinks(searchUrl string, addr string, port string, timeout int) {
	var torProxy string = "socks5://" + addr + ":" + port
	torProxyUrl, err := url.Parse(torProxy)
	if err != nil {
		log.Fatal("Error parsing URL: ", err)
	}
	torTransport := &http.Transport{Proxy: http.ProxyURL(torProxyUrl)}
	client := &http.Client{Transport: torTransport, Timeout: time.Second * time.Duration(timeout)}
	resp, err := client.Head(searchUrl)
	if err != nil {
		log.Fatal("Error with GET request", err)
	}
	defer resp.Body.Close()
	bytes := resp.Body
	tokenizer := html.NewTokenizer(bytes)
	found_urls := make([]string, 0)
	for not_end := true; not_end; {
		currentTokenType := tokenizer.Next()
		switch {
		case currentTokenType == html.ErrorToken:
			not_end = false
		case currentTokenType == html.StartTagToken:
			token := tokenizer.Token()
			if token.Data == "a" {
				attributes := token.Attr
				for i := 0; i < len(attributes); i++ {
					if attributes[i].Key == "href" {
						found_urls = append(found_urls, attributes[i].Val)
					}
				}
			}
		}
	}
	fmt.Printf("Number of URLs found: %v\n", len(found_urls))
	for _, link := range found_urls {
		_, err := url.ParseRequestURI(link)
		if err != nil {
			continue
		}
		wg.Add(1)
		go asyncHead(client, link)
	}
	wg.Wait()
}

func main() {
}

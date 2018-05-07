package main

import "C"

import (
	"fmt"
	"log"
	"net/http"
	"net/url"
	"regexp"
	"sync"
	"time"

	"golang.org/x/net/html"
)

// Checks for valid .onion domain names
func validOnionURL(url string) bool {
	pattern := `^https?:\/\/(www\.)?([a-z,A-Z,0-9]*)\.onion/(.*)`
	re := regexp.MustCompile(pattern)
	return re.Match([]byte(url))
}

// Used to perform ascynchrounous head requess
func asyncHead(client *http.Client, link string) {
	defer wg.Done()
	resp, err := client.Get(link)
	if err == nil && resp.StatusCode < 400 {
		fmt.Printf("%v is reachable.\n", link)
	} else {
		fmt.Printf("%v is not reachable.\n", link)
	}
}

// Parses html attributes to find urls
func parseUrls(attributes []html.Attribute) []string {
	var foundUrls = make([]string, 0)
	for i := 0; i < len(attributes); i++ {
		if attributes[i].Key == "href" && validOnionURL(attributes[i].Val) {
			foundUrls = append(foundUrls, attributes[i].Val)
		}
	}
	return foundUrls
}

// Establishes tor connection for tcp
func setupTor(addr string, port string, timeout int) *http.Client {
	var torProxy = "socks5://" + addr + ":" + port
	torProxyURL, err := url.Parse(torProxy)
	if err != nil {
		log.Fatal("Error parsing URL: ", err)
	}
	torTransport := &http.Transport{Proxy: http.ProxyURL(torProxyURL)}
	return &http.Client{Transport: torTransport, Timeout: time.Second * time.Duration(timeout)}
}

var wg sync.WaitGroup

//export GetLinks
func GetLinks(searchURL string, addr string, port string, timeout int) {
	var client = setupTor(addr, port, timeout)
	resp, err := client.Get(searchURL)
	if err != nil {
		log.Fatal("Error with GET request", err)
	}
	defer resp.Body.Close()
	bytes := resp.Body
	tokenizer := html.NewTokenizer(bytes)
	var urls []string
	var found []string
	for notEnd := true; notEnd; {
		currentTokenType := tokenizer.Next()
		switch {
		case currentTokenType == html.ErrorToken:
			notEnd = false
		case currentTokenType == html.StartTagToken:
			token := tokenizer.Token()
			if token.Data == "a" {
				attributes := token.Attr
				found = parseUrls(attributes)
				urls = append(urls, found...)
			}
		}
	}
	fmt.Printf("Number of URLs found: %v\n", len(urls))
	for _, link := range urls {
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

package main

import "testing"

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

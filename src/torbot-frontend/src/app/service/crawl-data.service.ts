import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class CrawlDataService {

  constructor(
    private http:HttpClient
  ) { }

  getCrawlData(crawl){
    console.log("Iinside service",crawl);
    
    return this.http.post("http://127.0.0.1:5000/postApi", crawl)
  }
}

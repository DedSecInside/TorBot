import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-crawl-url',
  templateUrl: './crawl-url.component.html',
  styleUrls: ['./crawl-url.component.css']
})
export class CrawlUrlComponent implements OnInit {


  inputURL='';
  advanceSearch = false;
  constructor() { }

  ngOnInit(): void {
  }
  getCrawledData(){
    console.log(this.inputURL);
    
  }
  enableAdvanceSearch(){
    this.advanceSearch = true;
  }
}

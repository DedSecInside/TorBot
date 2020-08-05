import { Component, OnInit } from '@angular/core';
import { Options } from 'ng5-slider';


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

  value: number = 100;
      options: Options = {
      floor: 0,
      ceil: 100
      };

  getCrawledData(){
    console.log(this.inputURL);
    
  }
  enableAdvanceSearch(){
    this.advanceSearch = true;
  }
}



import { Component, OnInit } from '@angular/core';
import { Options } from 'ng5-slider';
import { CrawlDataService } from '../service/crawl-data.service';
import { NgxSpinnerService } from "ngx-spinner";
import { Router } from '@angular/router';
export class Crawl{
  constructor(
    public ip: String,
    public port : number,
    public no_socks : Boolean,
    public url : String,
    //public gather : Boolean,
    public version : Boolean,
    //public update : Boolean,
    public mail : Boolean,
    public info : Boolean,
    public save : Boolean,
    public depth : Number,
    public download: Boolean
  ){}
}

@Component({
  selector: 'app-crawl-url',
  templateUrl: './crawl-url.component.html',
  styleUrls: ['./crawl-url.component.css']
})
export class CrawlUrlComponent implements OnInit {


  inputURL='';
  advanceSearch = false;
  isVersion =false;
  isMail =false;
  isSave = false;
  isDownload = false;
  isNosocks = false;
  isInfo = false;
  alterIP='127.0.0.1';
  alterPort=9050;
  value: number = 0;
  options: Options = {
  floor: 0,
  ceil: 100
  };

  crawlData:Crawl
  outData:any


  constructor(
    private crawlDataService:CrawlDataService,
    private spinner: NgxSpinnerService,
    private router:Router
  ) { }

  ngOnInit(): void {
    this.crawlData=new Crawl(this.alterIP,this.alterPort,this.isNosocks,this.inputURL,this.isVersion,this.isMail,this.isInfo,this.isSave,this.value,this.isDownload);
  }


  getCrawledData(){
    this.crawlData.ip=this.alterIP;
    this.crawlData.port=this.alterPort;
    this.crawlData.no_socks=this.isNosocks;
    this.crawlData.url=this.inputURL;
    this.crawlData.version=this.isVersion;
    this.crawlData.mail=this.isMail;
    this.crawlData.info=this.isInfo;
    this.crawlData.save=this.isSave;
    this.crawlData.depth=this.value;
    this.crawlData.download=this.isDownload;
    //console.log(this.crawlData)
    //console.log(this.inputURL);
    //console.log(this.isVersion,this.isMail,this.isDownload,this.isInfo,this.isNosocks,this.isSave,this.value);
    this.spinner.show();
    this.crawlDataService.getCrawlData(this.crawlData).subscribe(
      data=>{
        console.log(data);
        this.outData=data
        this.spinner.hide();
        this.advanceSearch = false;
      },
      error=>{
        this.spinner.hide();
        this.router.navigate(['**'])
      }
    )
    
  }
  enableAdvanceSearch(){
    this.advanceSearch = true;
  }
}



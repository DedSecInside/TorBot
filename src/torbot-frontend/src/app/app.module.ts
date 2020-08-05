import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Ng5SliderModule } from 'ng5-slider';


import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CrawlUrlComponent } from './crawl-url/crawl-url.component';

@NgModule({
  declarations: [
    AppComponent,
    CrawlUrlComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    Ng5SliderModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

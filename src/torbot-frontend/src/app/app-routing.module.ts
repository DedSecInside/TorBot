import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CrawlUrlComponent } from './crawl-url/crawl-url.component';
import { ErrorComponent } from './error/error.component';

const routes: Routes = [
  {path:'',component:CrawlUrlComponent},
  {path:'**',component:ErrorComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

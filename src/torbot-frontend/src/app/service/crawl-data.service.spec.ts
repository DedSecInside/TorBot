import { TestBed } from '@angular/core/testing';

import { CrawlDataService } from './crawl-data.service';

describe('CrawlDataService', () => {
  let service: CrawlDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CrawlDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

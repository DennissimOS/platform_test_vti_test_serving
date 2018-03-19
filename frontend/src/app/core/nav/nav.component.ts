import {Component, Inject} from '@angular/core';
import {TranslateService} from '@ngx-translate/core';

import {APP_CONFIG, AppConfig} from '../../config/app.config';
import {IAppConfig} from '../../config/iapp.config';
import {ProgressBarService} from '../progress-bar.service';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.scss']
})

export class NavComponent {
  appConfig: any;
  menuItems: any[];
  progressBarMode: string;
  currentLang: string;

  constructor(@Inject(APP_CONFIG) appConfig: IAppConfig,
              private progressBarService: ProgressBarService,
              private translateService: TranslateService) {
    this.appConfig = appConfig;
    this.loadMenus();
    this.currentLang = this.translateService.currentLang;

    this.progressBarService.updateProgressBar$.subscribe((mode: string) => {
      this.progressBarMode = mode;
    });
  }

  changeLanguage(language: string): void {
    this.translateService.use(language).subscribe(() => {
      this.loadMenus();
    });
  }

  private loadMenus(): void {
    this.translateService.get(['home', 'buildList', 'jobList', 'deviceList', 'scheduleList'], {}).subscribe((texts: any) => {
      this.menuItems = [
        {link: '/', name: texts['home']},
        {link: '/' + AppConfig.routes.builds, name: texts['buildList']},
        {link: '/' + AppConfig.routes.jobs, name: texts['jobList']},
        {link: '/' + AppConfig.routes.devices, name: texts['deviceList']},
        {link: '/' + AppConfig.routes.schedules, name: texts['scheduleList']}
      ];
    });
  }
}

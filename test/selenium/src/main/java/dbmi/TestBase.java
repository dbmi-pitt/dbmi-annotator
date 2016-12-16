package dbmi;

//import static org.junit.Assert.*;

import java.util.List;
import java.util.concurrent.TimeUnit;
/*
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;

import org.junit.Test;
*/

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.ie.InternetExplorerDriver;

import org.testng.annotations.*;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Properties;

/** 
	this is a base class and contains no test, alll test inherit from this 
	class mainly for the beforeClass and afterClass methods
**/
public class TestBase {
	public StringBuffer verificationErrors = new StringBuffer();
	public WebDriver driver;
	String browser;
	String appUrl;
	static int timeoutLimit = 100;

	@BeforeClass
	public void beforeClass() {
		// Firefox driver is included in the s selenium-server-stanalone.jar 
		// available in the downloads. The driver comes in the form of an xpi (firefox extension) 
		// which is added to the firefox profile when you start a new instance of FirefoxDriver.
		//
		// driver = new FirefoxDriver();

		//System.setProperty("webdriver.chrome.driver", "res/chromedriver.exe");
		//driver = new ChromeDriver();

		// note: the 64-bit version of this has some slowness issues, use the 32bit verison
		// System.setProperty("webdriver.ie.driver", "res/IEDriverServer.exe");
		// driver = new InternetExplorerDriver();
		// driver.get("http://localhost/RiskViewer/");
		// driver.manage().timeouts().pageLoadTimeout(1000, TimeUnit.SECONDS);

		
		browser = System.getProperty("browser");
		appUrl = System.getProperty("app.base.url");
		
		if (browser.equals("ie")) {
			System.setProperty("webdriver.ie.driver", "res/IEDriverServer.exe"); 
			driver = new InternetExplorerDriver();			
		} else if (browser.equals("chrome")) {
			System.setProperty("webdriver.chrome.driver", "/home/yin2/dbmi-annotator/test/selenium/libs/chromedriver"); 
            driver = new ChromeDriver();
		} else {
            System.setProperty("webdriver.gecko.driver", "/usr/bin/geckodriver");
			driver = new FirefoxDriver();
		}
		driver.get(appUrl);
		driver.manage().timeouts().pageLoadTimeout(1000, TimeUnit.SECONDS);

	}
	@AfterClass
	public void afterClass() {
		driver.quit();
	}

// 	// click on Expand		
// 	protected void clickExpand(){

//         driver.findElement(By.id("expand")).clear();
//         driver.findElement(By.id("expand")).clear();
//         driver.findElement(By.id("expand")).sendKeys("VFUR");
// //	        driver.findElement(By.name("search")).click();
// //	        driver.findElement(By.name("search")).click();
       
//     	List<WebElement> list2 = driver.findElements(By.xpath("//input[@id='expand']"));
//         driver.manage().timeouts().pageLoadTimeout(100, TimeUnit.SECONDS);
        
//         if(!list2.isEmpty())
//         {
// 			driver.findElement(By.xpath("//input[@id='expand']")).click();
// 			driver.manage().timeouts().pageLoadTimeout(1000, TimeUnit.SECONDS);
//         }
        
//         if(!list2.isEmpty())
//         {
//             driver.findElement(By.xpath("//a[contains(text(),'Select')]")).click();
//             driver.manage().timeouts().pageLoadTimeout(100, TimeUnit.SECONDS);
//         }
//         else
//         {
//         	clickExpand();
//         }
//     }


}

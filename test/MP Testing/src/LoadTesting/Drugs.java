package LoadTesting;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;

/**
 *@author
 *@date:Jun 5, 201610:40:09 PM
 *
 */
public class Drugs {

    public static void main(String[] args) throws InterruptedException {
        //create firefox driver object
        WebDriver driver = new FirefoxDriver();
        
        //create chrome driver object
        //System.setProperty("webdriver.chrome.driver", "/Users/runy1/Downloads/chromedriver");
        //WebDriver driver = new ChromeDriver();
        driver.get("http://130.49.206.139/dbmiannotator");
        
        Thread.sleep(3000);
        driver.findElement(By.linkText("Login")).click();
        
        Thread.sleep(3000);
        driver.findElement(By.name("email")).sendKeys("123@123.com");
        driver.findElement(By.name("password")).sendKeys("78909l");
        
        Thread.sleep(3000);
        driver.findElement(By.xpath("//button[contains(.,'Login')]")).click();

        Thread.sleep(3000);
        driver.findElement(By.linkText("PMC1865122")).click();
        
        
    }

}

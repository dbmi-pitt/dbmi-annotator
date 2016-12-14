package dbmi;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.*;

/**
 *@author: Yifan Ning
 *@date: Dec 13, 2016 5:01:32 PM
 *
 */
public class Login extends TestBase{


    @Test
    public void test_user_login() throws InterruptedException {        
        driver.get(appUrl);
        Thread.sleep(3000);
        driver.findElement(By.linkText("Login")).click();
        Thread.sleep(3000);
        driver.findElement(By.name("email")).sendKeys("test@gmail.com");
        driver.findElement(By.name("password")).sendKeys("testtest");
        Thread.sleep(3000);
        driver.findElement(By.xpath("//button[contains(.,'Login')]")).click();
        Thread.sleep(3000);
        driver.findElement(By.linkText("Logout")).click();
    }

    @Test
    public void test_user_register() throws InterruptedException {

        driver.get(appUrl);        
        Thread.sleep(3000);
        driver.findElement(By.linkText("Register")).click();        
        Thread.sleep(3000);
        driver.findElement(By.name("email")).sendKeys("test@gmail.com");
        driver.findElement(By.name("username")).sendKeys("tester");
        driver.findElement(By.name("password")).sendKeys("testtest");
        driver.findElement(By.name("repassword")).sendKeys("testtest");
        
        Thread.sleep(3000);
        driver.findElement(By.xpath("//button[contains(.,'Register')]")).click();
        Thread.sleep(3000);
    }


}

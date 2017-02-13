package dbmi;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.testng.annotations.*;

import org.openqa.selenium.WebElement;
import org.openqa.selenium.remote.RemoteWebDriver;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.interactions.Action;
import org.openqa.selenium.Dimension;

/**
 *@author: Yifan Ning
 *@date: Dec 13, 2016 5:01:32 PM
 *
 */
public class Login extends TestBase{


    @Test
    public void test_user_login() throws InterruptedException {        
        driver.get(appUrl);
        Thread.sleep(800);
        driver.findElement(By.linkText("Login")).click(); // click login 
        Thread.sleep(500);
        driver.findElement(By.name("email")).sendKeys("test@gmail.com"); // fill username
        driver.findElement(By.name("password")).sendKeys("testtest"); // fill password
        Thread.sleep(500);
        driver.findElement(By.xpath("//button[contains(.,'Login')]")).click(); // submit 
        Thread.sleep(1000);
        // driver.findElement(By.linkText("Logout")).click(); // logout

        // load test PMC article
        driver.findElement(By.name("sourceURL")).sendKeys("http://localhost/PMC/PMCTEST.html");
        driver.findElement(By.xpath("//button[contains(.,'load')]")).click();
        Thread.sleep(1500);

        // import existing annotations
        driver.findElement(By.xpath("//button[contains(.,'Import')]")).click(); // import
        Thread.sleep(1000);

        // // create drug mention 1
        // Actions action1 = new Actions(driver);

        // WebElement drug1Ele = driver.findElement(By.id("drug1-in-p1"));
        // System.out.println(drug1Ele.getText());     
        // System.out.println(drug1Ele.getLocation());     

        // action1.doubleClick(drug1Ele).build().perform();
        // Thread.sleep(1000);
        // driver.findElement(By.className("hl-adder-btn")).click(); // submit 

        // // refresh
        // Thread.sleep(2000);
        // driver.navigate().refresh();
        // Thread.sleep(1000);
        // driver.findElement(By.xpath("//button[contains(.,'Import')]")).click(); // import
        // Thread.sleep(1000);

        // // create drug mention 2
        // Actions action2 = new Actions(driver);
        // WebElement drug2Ele = driver.findElement(By.id("drug2-in-p1"));
        // System.out.println(drug2Ele.getText());     
        // System.out.println(drug2Ele.getLocation());     

        // action2.doubleClick(drug2Ele).build().perform();
        // Thread.sleep(1000);       
        // driver.findElement(By.className("hl-adder-btn")).click(); // submit

        // // refresh
        // Thread.sleep(2000);
        // driver.navigate().refresh();
        // Thread.sleep(1000);
        // driver.findElement(By.xpath("//button[contains(.,'Import')]")).click(); // import
        // Thread.sleep(1000);


        WebElement claim1 = driver.findElement(By.id("claim-text-1"));
        WebElement claim2 = driver.findElement(By.id("claim-text-2"));

        System.out.println(claim1.getLocation());     
        System.out.println(claim2.getLocation());     

        Actions action3 = new Actions(driver);
        //action3.dragAndDrop(claim1, claim2).build().perform();
        //action3.moveToElement(claim1).clickAndHold().moveToElement(claim2).release().build().perform();

        //Action select = action3.clickAndHold(driver.findElement(By.id("drug1-in-p1"))).moveToElement(driver.findElement(By.id("drug2-in-p1"))).release(driver.findElement(By.id("drug2-in-p1"))).build();
        //select.perform();
        
        //WebElement pEle = driver.findElement(By.id("__p1")); // get first p   
        //action.moveToElement(drug1Ele).clickAndHold().moveToElement(drug2Ele).release().build().perform();

        // Action select = action3.clickAndHold(drug1Ele).moveToElement(drug2Ele).release(drug2Ele).build();
        // select.perform();

        //action3.dragAndDrop(, ).build().perform();
        Thread.sleep(500000);

    }

    public void ClickHold(WebElement element)
    {
        //Actions action = new Actions(driver);
        //action.doubleClick(element).build().perform();
        //action.moveByOffset(255,368).doubleClick().build().perform();

        //WebElement firstP = driver.findElement(By.xpath("/html/body/div[9]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[3]/div[1]/div[1]/div[3]/div[2]/div[1]/p[1]"));
        //WebElement firstP = driver.findElement(By.xpath("//p[text()='ketoconazole']"));

        

        // System.out.println(firstP.getText());     
        // System.out.println(firstP.getLocation());      

        // int x = firstP.getLocation().getX();
        // int y = firstP.getLocation().getY();

        // Actions action = new Actions(driver);
        // action.moveByOffset(x, y).doubleClick().build().perform();

        //action.moveByOffset(68,568).clickAndHold().moveByOffset(168,568).perform();
        //Thread.sleep(2000);
        //actions.MoveToElement(element).Release();
    }

    // @Test
    // public void test_user_register() throws InterruptedException {

    //     driver.get(appUrl);        
    //     Thread.sleep(2000);
    //     driver.findElement(By.linkText("Register")).click();        
    //     Thread.sleep(2000);
    //     driver.findElement(By.name("email")).sendKeys("test@gmail.com");
    //     driver.findElement(By.name("username")).sendKeys("tester");
    //     driver.findElement(By.name("password")).sendKeys("testtest");
    //     driver.findElement(By.name("repassword")).sendKeys("testtest");
        
    //     Thread.sleep(2000);
    //     driver.findElement(By.xpath("//button[contains(.,'Register')]")).click();
    //     Thread.sleep(2000);
    // }


}

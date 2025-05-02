from ..modules import run_test

def count_coins(coins):
    coins = coins.split(",")
    coin200 = float(coins[0])*200
    coin100 = float(coins[1])*100
    coin50 = float(coins[2])*50
    coin20 = float(coins[3])*20
    coin10 = float(coins[4])*10
    coin5 = float(coins[5])*5
    coin2 = float(coins[6])*2
    coin1 = float(coins[7])
    coin05 = float(coins[8])*0.5
    coin025 = float(coins[9])*0.25
    coin01 = float(coins[10])*0.1
    coin005 = float(coins[11])*0.05

    return f"Total: R$ {coin200 + coin100 + coin50 + coin20 + coin10 + coin5 + coin2 + coin1 + coin05 + coin025 + coin01 + coin005:.2f}"

if __name__ == "__main__":
    run_test(count_coins, "1,2,3,4,5,6,7,8,9,10,11,12")
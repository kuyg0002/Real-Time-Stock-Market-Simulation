import graphene

# Define the Stock type with its fields
class Stock(graphene.ObjectType):
    name = graphene.String()
    ticker_symbol = graphene.String()
    current_price = graphene.Float()
    historical_price_data = graphene.List(graphene.Float)
    highest_price = graphene.Float()
    lowest_price = graphene.Float()
    trading_volume = graphene.Int()

# Define the main query class
class Query(graphene.ObjectType):
    stock = graphene.Field(Stock, ticker_symbol=graphene.String())

    def resolve_stock(self, info, ticker_symbol):
        # Here you'd fetch the stock data from your SQLite3 DB using the provided ticker_symbol
        # For the sake of this example, let's return dummy data
        return Stock(
            name="Dummy Stock",
            ticker_symbol=ticker_symbol,
            current_price=100.50,
            historical_price_data=[95.0, 96.5, 98.0, 100.5],
            highest_price=105.0,
            lowest_price=90.0,
            trading_volume=10000
        )

schema = graphene.Schema(query=Query)

# You can add a small test here to ensure things are working
if __name__ == "__main__":
    # A simple query to fetch a stock by its ticker symbol
    query_string = '''
    {
      stock(tickerSymbol: "DUMMY") {
        name
        currentPrice
      }
    }
    '''
    result = schema.execute(query_string)
    print(result.data)

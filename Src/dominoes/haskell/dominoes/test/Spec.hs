import Test.Hspec

main :: IO()
main = hspec $ do
  describe "Dummy 1" $ do
    it "should be equal" $ do (1::Int) `shouldBe` (1::Int)
  describe "Dummy 2" $ do
    it "should be equal" $ do (1::Int) `shouldBe` (0::Int)


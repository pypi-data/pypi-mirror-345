モジュール
==========

**補足**

ページの補足説明


Module1
-------

**補足**

モジュールの補足説明

モジュールの説明

.. vb:function:: Sub procedureWithoutDocComment()
   :module: Module1


**補足**

- 関数の補足説明1
- 関数の補足説明2


.. vb:function:: Sub sampleProcedure()
   :module: Module1

   かんたんなプロシージャ

.. vb:function:: Private Sub samplePrivateProcedure(ByVal num As Integer)
   :module: Module1

   かんたんなプライベートプロシージャ

   :param num: 数字
   :type num: Integer

.. vb:function:: Function sampleFunction(ByVal name As String) As String
   :module: Module1

   名前を呼ぶ文字列を返す関数
   名前を入力すると「こんにちは、○○さん」を出力する。

   :param name: 名前
   :type name: String
   :returns: 名前を呼ぶ文字列
   :rtype: String

   注意事項1
   注意事項2
   
   注意事項3

.. vb:function:: Sub testFix(ByVal name)
   :module: Module1

   修正確認用

   :param name: 名前

   注意事項

.. vb:function:: Sub testFix2(name)
   :module: Module1

   修正確認用2

   :param name: 名前

   注意事項


モジュール1
-----------

モジュールの説明

.. vb:function:: Sub procedureWithoutDocComment()
   :module: モジュール1

.. vb:function:: Sub sampleProcedure()
   :module: モジュール1

   かんたんなプロシージャ

.. vb:function:: Private Sub samplePrivateProcedure(ByVal num As Integer)
   :module: モジュール1

   かんたんなプライベートプロシージャ

   :param num: 数字
   :type num: Integer

.. vb:function:: Function 名前呼び(ByVal name As String) As String
   :module: モジュール1

   名前を呼ぶ文字列を返す関数
   名前を入力すると「こんにちは、○○さん」を出力する。

   :param name: 名前
   :type name: String
   :returns: 名前を呼ぶ文字列
   :rtype: String

   注意事項1
   注意事項2
   
   注意事項3


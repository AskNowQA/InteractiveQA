package tech.sda.benchmark;

import java.util.List;

import tech.sda.interactiveqa.Nqs;
import tech.sda.interactiveqa.Parser;
import tech.sda.util.annotation.QueryAnnotaion;

public class BenchmarkEvalution {

	public static void main(String[] args)
	{
		for(int i=0;i<349;i++)
		{	System.out.print((i+1)+"**");
		evaluate(i);

		}
	}
	static void evaluate(int n)
	{
		List<Nqs> templates = Parser.parse();
		Nqs q1 = templates.get(n);
		System.out.print(q1.nlQuery +"**");
		QueryAnnotaion.annotate(q1);
		System.out.println();
	}
}

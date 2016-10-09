package tech.sda.iqa.util.annotation;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.Set;

import tech.sda.iqa.sparql.OneHopRelationQuery;
import tech.sda.iqa.util.request_server;

public class PredicateAnnotator {

	public static Set<String> annotate(Set<String> predicateCandidate, Set<String> resourceSpotlight) {
		// TODO Auto-generated method stub
		Iterator iter1 = predicateCandidate.iterator();
		String first = (String) iter1.next();
		String pc =  first;
		
		Iterator iter2 = resourceSpotlight.iterator();
		String res = (String) iter2.next();
		 
		
		getAnnotaion(pc,res);
		return null;
	}

	private static void getAnnotaion(String pc, String res) {
		// TODO Auto-generated method stub
		ArrayList<String[]> Triple = new ArrayList<String[]>(); //To store 1.uriOfPredicate 2.LabelOfPredicate 3.ScoreFromWord2vec
		ArrayList<String[]> listOfPair = new ArrayList<String[]>(); 
		String score = null; //listOfPair + Score = Triple
		listOfPair = OneHopRelationQuery.getPredicateList(res);
		float temp = 0, highest =-1; 
		String higestmatchedRel="";
		for (int i = 0; i < listOfPair.size(); i++){
			String p[] = listOfPair.get(i);
			System.out.println(p[0]+"::"+p[1]);
			try {
				temp=request_server.sendToVec(p[1],pc);
				if(temp>highest){
					highest=temp;
					higestmatchedRel = p[0]+p[1];
					}
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			score=String.valueOf(temp);
			Triple.add(new String[] {p[0], p[1],score});
		}
		System.out.println("highest:: "+higestmatchedRel);
		
		
	}

}

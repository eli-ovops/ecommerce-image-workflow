import Foundation
import CoreText
import CoreGraphics
let b=URL(fileURLWithPath:CommandLine.arguments[1]);let entries=try JSONSerialization.jsonObject(with:Data(contentsOf:b.appendingPathComponent("title-strings.json"))) as! [[String:Any]]
var result=[String:String]()
for e in entries {let text=e["text"] as! String;let size=e["size"] as! Double;let font=CTFontCreateWithName("PingFangSC-Semibold" as CFString,size,nil);let line=CTLineCreateWithAttributedString(NSAttributedString(string:text,attributes:[NSAttributedString.Key(kCTFontAttributeName as String):font]));var d=""
 for rr in CTLineGetGlyphRuns(line) as! [CTRun] {let n=CTRunGetGlyphCount(rr);var gs=[CGGlyph](repeating:0,count:n);var ps=[CGPoint](repeating:.zero,count:n);CTRunGetGlyphs(rr,CFRange(location:0,length:0),&gs);CTRunGetPositions(rr,CFRange(location:0,length:0),&ps)
  for i in 0..<n {if let p=CTFontCreatePathForGlyph(font,gs[i],nil){let off=ps[i];p.applyWithBlock{ptr in let e=ptr.pointee;func pt(_ j:Int)->String{"\(e.points[j].x+off.x),\(-e.points[j].y-off.y)"};switch e.type {case .moveToPoint:d+="M"+pt(0);case .addLineToPoint:d+="L"+pt(0);case .addQuadCurveToPoint:d+="Q"+pt(0)+" "+pt(1);case .addCurveToPoint:d+="C"+pt(0)+" "+pt(1)+" "+pt(2);case .closeSubpath:d+="Z";@unknown default:break}}}}
 }
 result["\(Int(size))|\(text)"]=d
}
try JSONSerialization.data(withJSONObject:result).write(to:b.appendingPathComponent("title-paths.json"))

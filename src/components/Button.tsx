//Importing the IconType from react-icons to define the type of icon which is passed as a prop
import { IconType } from "react-icons";

interface Props {
  icon: IconType;
  onClick: () => void;
}
//Button component that takes 'icon' and 'onClick' as props
const Button = ({ icon: Icon, onClick }: Props) => {
  return (
    //The buttom element triggers the 'onClick' function when clicked
    <button
      onClick={onClick}
      style={{
        padding: "8px", //Added padding inside button
        border: "none",
        backgroundColor: "transparent",
        cursor: "pointer",
        borderRadius: "50%", //Makes the button circular by rounding edges
      }}
    >
      <Icon size={50} />
    </button>
  );
};

export default Button;
